from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import Optional

from core.dependencies import get_db_session, get_current_user_session
from database.models import User, UserRead

from pydantic import BaseModel

class UpdateCategoryInstructionRequest(BaseModel):
    category_instruction: Optional[str] = None

router = APIRouter(prefix="/api/users", tags=["User Settings"])

@router.put("/me/settings/category-instruction", response_model=UserRead)
async def update_user_category_instruction(
    request_data: UpdateCategoryInstructionRequest,
    session_data: dict = Depends(get_current_user_session),
    db: Session = Depends(get_db_session),
):
    user_id = session_data.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    db_user = db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db_user.category_instruction = request_data.category_instruction
    
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        print(f"Error committing category instruction update for user {user_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not save settings.")

    return db_user


@router.get("/me", response_model=UserRead)
async def get_current_user_details(
    session_data: dict = Depends(get_current_user_session),
    db: Session = Depends(get_db_session),
):
    user_id = session_data.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    db_user = db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return db_user