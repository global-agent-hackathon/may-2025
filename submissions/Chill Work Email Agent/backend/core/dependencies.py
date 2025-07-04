from fastapi import Request, HTTPException, Depends
from sqlmodel import Session

from database.session import engine

def get_db_session():
    with Session(engine) as session:
        yield session

async def get_current_user_session(
    request: Request,
) -> dict:
    user_id = request.session.get("user_id")
    session_access_token = request.session.get("access_token")

    if not user_id or not session_access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return {
        "user_id": user_id,
        "access_token": session_access_token,
        "user_info": request.session.get("user")
    }