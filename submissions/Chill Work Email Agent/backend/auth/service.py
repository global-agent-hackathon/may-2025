import httpx
from typing import Optional
from sqlmodel import Session, select
from fastapi import HTTPException, Request

from core.config import settings
from database.models import User, ProviderType

async def exchange_code_for_token(code: str) -> dict:
    token_data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    async with httpx.AsyncClient() as client:
        try:
            token_response = await client.post(settings.TOKEN_URL, data=token_data)
            token_response.raise_for_status()
            return token_response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error exchanging code for token: {e.response.text}")
            raise HTTPException(status_code=400, detail="Failed to exchange authorization code for token.")
        except httpx.RequestError as e:
            print(f"Request error while exchanging code for token: {e}")
            raise HTTPException(status_code=503, detail="Could not connect to authentication provider.")

async def get_google_user_info(access_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            userinfo_response = await client.get(settings.USERINFO_URL, headers=headers)
            userinfo_response.raise_for_status()
            return userinfo_response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error fetching user info. Status: {e.response.status_code}, Response: {e.response.text}")
            raise HTTPException(status_code=400, detail="Failed to fetch user information from provider.")
        except httpx.RequestError as e:
            print(f"Request error while fetching user info: {e}")
            raise HTTPException(status_code=503, detail="Could not connect to provider to get user info.")

def get_or_create_user(db: Session, user_info: dict, access_token: str, refresh_token: Optional[str]) -> User:
    google_email = user_info.get("email")
    google_provider_id = user_info.get("sub") or user_info.get("id") # "sub" is important
    google_name = user_info.get("name")
    google_picture = user_info.get("picture")

    if not google_email or not google_provider_id:
        print(f"ERROR: Essential user information (email or ID) not found. UserInfo received: {user_info}")
        raise HTTPException(status_code=400, detail="Essential user information (email or ID) not found from provider.")

    statement = select(User).where(User.provider_id == google_provider_id, User.provider_type == ProviderType.GOOGLE)
    db_user = db.exec(statement).first()

    if db_user:
        print(f"User found (ID: {db_user.id}, Email: {db_user.email}). Updating details.")
        db_user.email = google_email
        db_user.name = google_name
        db_user.picture = google_picture
        db_user.access_token = access_token
        if refresh_token:
            db_user.refresh_token = refresh_token
    else:
        print(f"New user (Email: {google_email}). Creating new record.")
        db_user = User(
            email=google_email,
            name=google_name,
            picture=google_picture,
            provider_type=ProviderType.GOOGLE,
            provider_id=google_provider_id,
            access_token=access_token,
            refresh_token=refresh_token,
            is_active=True
        )
    
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
        print(f"User (ID: {db_user.id}) data saved/updated successfully.")
    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Could not save user information to the database.")
    
    return db_user