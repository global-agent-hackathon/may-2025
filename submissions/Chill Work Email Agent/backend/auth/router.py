from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
from sqlmodel import Session

from core.config import settings
from core.dependencies import get_db_session, get_current_user_session
from . import service as auth_service

router = APIRouter()

@router.get("/login")
async def login_via_google(request: Request):
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(settings.SCOPES),
        "access_type": "offline",
        "prompt": "consent",
    }
    auth_url = f"{settings.AUTHORIZATION_URL}?{urlencode(params)}"
    return RedirectResponse(url=auth_url)

@router.get("/auth/callback")
async def auth_callback(
    request: Request,
    code: str = None,
    error: str = None,
    db: Session = Depends(get_db_session)
):
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth Error: {error}")
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    token_json = await auth_service.exchange_code_for_token(code)
    access_token = token_json.get("access_token")
    id_token_str = token_json.get("id_token")
    refresh_token = token_json.get("refresh_token")

    if not access_token:
        raise HTTPException(status_code=400, detail="Access token not found in response")

    user_info_payload = await auth_service.get_google_user_info(access_token)

    db_user = auth_service.get_or_create_user(db, user_info_payload, access_token, refresh_token)
    request.session["user_id"] = db_user.id
    request.session["access_token"] = access_token
    if id_token_str:
        request.session["id_token"] = id_token_str
        request.session["refresh_token"] = refresh_token
    
    request.session["user"] = {
        "id" : db_user.id,
        "email": db_user.email,
        "name": db_user.name,
        "picture": db_user.picture,
    }
    return RedirectResponse(url=settings.FRONTEND_DASHBOARD_URL, status_code=307)


@router.get("/get-user-data")
async def get_logged_in_user_info(session_data: dict = Depends(get_current_user_session)):
    return session_data["user_info"]

@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return {"message": "Successfully logged out"}