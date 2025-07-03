"""
Conversation management endpoints

This module handles conversation CRUD operations:
- Create a new conversation
- Get a conversation by ID
- List user conversations
- Delete a conversation
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

# Import database operations
from database_storage import (
    delete_conversation,
    get_conversation,
    get_user_conversations,
)

# Import common utilities
from .common import (
    ConversationResponse,
    get_current_user,
    get_session,
)

# Create router without prefix (it will be added by the parent router)
router = APIRouter()


@router.delete("/conversation/{conversation_id}", status_code=204)
async def delete_conversation_route(
    conversation_id: str,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Delete a conversation"""
    conversation = await get_conversation(session, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Ensure the user has access to this conversation
    if conversation["user_id"] != user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this conversation"
        )

    success = await delete_conversation(session, conversation_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete conversation")

    # Return no content on success
    return None


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_user_conversations_route(
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    limit: int = Query(
        20, ge=1, le=100, description="Maximum number of conversations to return"
    ),
    offset: int = Query(
        0, ge=0, description="Number of conversations to skip (for pagination)"
    ),
):
    """
    Get all conversations for the current user

    Supports pagination with limit and offset parameters.
    Results are sorted by updated_at in descending order (newest first).
    """
    conversations = await get_user_conversations(
        session, user.id, limit=limit, offset=offset
    )
    return [ConversationResponse(**c) for c in conversations]
