import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from utils import config, get_logger

from .auth import (
    authenticate_user_google,
    get_current_user,
    get_db,
    get_google_auth_url,
)
from .models import User

# Initialize logger
logger = get_logger("adgenius.oauth")

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login/google")
async def login_google(request: Request, redirect_url: Optional[str] = None):
    """
    Generate Google OAuth login URL
    If redirect_url is provided, it will be saved in state to redirect after authentication
    """
    state = None
    if redirect_url:
        # Encode the redirect URL in the state parameter
        state = json.dumps({"redirect_url": redirect_url})
        logger.info(f"Google OAuth login with redirect URL: {redirect_url}")
    else:
        logger.info("Google OAuth login initiated without redirect URL")

    auth_url = get_google_auth_url(state=state)
    return {"auth_url": auth_url}


@router.get("/callback")
async def auth_callback(
    code: str, state: Optional[str] = None, session: AsyncSession = Depends(get_db)
):
    """
    Handle the OAuth callback from Google
    Exchanges the code for tokens and creates a user session
    """
    logger.info("Received OAuth callback from Google")
    try:
        # Exchange code for tokens and get user info
        logger.debug(f"Exchanging authorization code for token, state: {state}")
        token_data = await authenticate_user_google(code, session)

        # Create response with JWT token
        user = token_data["user"]
        logger.info(f"User authenticated successfully: {user.email}")

        # Handle redirection if state contains redirect_url
        redirect_url = "/"
        if state:
            try:
                state_data = json.loads(state)
                if "redirect_url" in state_data:
                    # Don't redirect to login page after successful login
                    if state_data["redirect_url"] == "/login":
                        redirect_url = "/"
                        logger.info(
                            "Avoiding redirect to login page, redirecting to home instead"
                        )
                    else:
                        redirect_url = state_data["redirect_url"]
                        logger.info(f"Redirecting to: {redirect_url}")
            except Exception as e:
                # If state parsing fails, use default redirect
                logger.warning(
                    f"Failed to parse OAuth state parameter during callback: {str(e)}",
                    extra={"state": state, "error": str(e), "code": code},
                )

        # Frontend URL from config
        frontend_url = config.frontend_url

        # Create the full redirect URL with auth token
        full_redirect_url = f"{frontend_url}/auth/callback?token={token_data['access_token']}&redirect={redirect_url}"
        logger.info(f"Redirecting to frontend: {full_redirect_url}")

        return RedirectResponse(url=full_redirect_url)
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Authentication failed: {str(e)}",
        )


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user"""
    logger.debug(f"User profile requested: {current_user.email}")
    return current_user


@router.post("/logout")
async def logout(request: Request, current_user: User = Depends(get_current_user)):
    """Logout user - with token-based auth, client handles token removal"""
    logger.info(f"User logged out: {current_user.email}")
    return JSONResponse(content={"success": True, "message": "Logged out successfully"})


@router.get("/validate")
async def validate_token(current_user: User = Depends(get_current_user)):
    """Validate token and return user if valid"""
    logger.debug(f"Token validated successfully for user: {current_user.email}")
    return {
        "valid": True,
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "photoURL": current_user.picture,
        },
    }
