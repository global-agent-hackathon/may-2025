"""
Draft Campaigns endpoints

This module handles fetching draft campaigns for a conversation.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database_storage import get_conversation, get_conversation_draft_campaigns
from database_storage.database import DraftCampaignTypes

from utils import get_logger

from .common import (
    get_current_user,
    get_session,
)

router = APIRouter()
logger = get_logger(__name__)


class DraftCampaignResponse(BaseModel):
    """Response model for a draft campaign"""

    id: str
    conversation_id: str
    type: DraftCampaignTypes
    data: dict
    created_at: str
    updated_at: str


@router.get(
    "/conversation/{conversation_id}/draft_campaigns",
    response_model=List[DraftCampaignResponse],
)
async def get_draft_campaigns_route(
    conversation_id: str,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get all draft campaigns for a conversation.
    """
    conversation = await get_conversation(session, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Ensure the user has access to this conversation
    if conversation["user_id"] != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this conversation"
        )

    draft_campaigns = await get_conversation_draft_campaigns(
        session=session, conversation_id=conversation_id
    )
    return [DraftCampaignResponse(**c) for c in draft_campaigns]
