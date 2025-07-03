from datetime import datetime, timedelta
from typing import Optional

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from utils.config import config

from .database import get_or_create_user, get_session, get_user_by_email
from .models import GoogleToken, GoogleUserInfo, TokenData, User, UserCreate

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

# Re-export get_session for dependency injection
get_db = get_session

# Google OAuth endpoints
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"

# Scopes for Google OAuth
SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid",
]


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=config.access_token_expire_minutes
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.secret_key, algorithm=config.algorithm)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)
) -> User:
    """Get the current user from the JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.secret_key, algorithms=[config.algorithm])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email, sub=email)
    except JWTError:
        raise credentials_exception
    user = None
    if token_data.email:
        user = await get_user_by_email(session, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


def get_google_auth_url(state: Optional[str]) -> str:
    """Generate the Google OAuth2 authorization URL"""
    params = {
        "client_id": config.google_client_id,
        "redirect_uri": config.google_redirect_uri,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
    }
    if state:
        params["state"] = state

    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return f"{GOOGLE_AUTH_URL}?{query_string}"


async def exchange_code_for_token(code: str) -> GoogleToken:
    """Exchange the authorization code for an access token"""
    data = {
        "code": code,
        "client_id": config.google_client_id,
        "client_secret": config.google_client_secret,
        "redirect_uri": config.google_redirect_uri,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(GOOGLE_TOKEN_URL, data=data)
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to retrieve token from Google",
            )

        return GoogleToken(**response.json())


async def get_google_user_info(token: GoogleToken) -> GoogleUserInfo:
    """Get the user information from Google using the access token"""
    headers = {"Authorization": f"Bearer {token.access_token}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(GOOGLE_USER_INFO_URL, headers=headers)
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to retrieve user info from Google",
            )

        return GoogleUserInfo(**response.json())


async def authenticate_user_google(code: str, session: AsyncSession):
    """Complete OAuth flow and return user with JWT token"""
    token = await exchange_code_for_token(code)
    user_info = await get_google_user_info(token)

    user_create = UserCreate(
        email=user_info.email,
        name=user_info.name,
        picture=user_info.picture,
        google_id=user_info.id,
    )

    user = await get_or_create_user(session, user_create)

    # Create access token for the user
    access_token_expires = timedelta(minutes=config.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer", "user": user}
