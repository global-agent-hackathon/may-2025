from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from core.dependencies import get_db_session, get_current_user_session
from . import service as gmail_sync_service

router = APIRouter(prefix="/api", tags=["gmail_sync"])

@router.post("/sync-mails", status_code=200)
async def sync_user_mails_endpoint(
    session_data: dict = Depends(get_current_user_session),
    db: Session = Depends(get_db_session)
):
    access_token = session_data["access_token"]
    user_id = session_data["user_id"]

    try:
        sync_results = await gmail_sync_service.sync_user_mails_logic(user_id, access_token, db)
        return {
            "message": "Mail sync process completed.",
            **sync_results
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Unexpected error in sync_user_mails_endpoint: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during mail synchronization.")