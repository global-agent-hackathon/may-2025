"""
Message handling endpoints

This module handles message operations:
- Add a message to a conversation
- Get messages for a conversation
"""

from datetime import UTC, datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

# Import database operations
from database_storage import (
    add_message,
    create_conversation,
    get_conversation,
    get_conversation_messages,
)

# Import common utilities
from .common import (
    MessageRequest,
    MessageResponse,
    get_current_user,
    get_session,
    logger,
)

# Create router without prefix (it will be added by the parent router)
router = APIRouter()


@router.post("/message", response_model=MessageResponse)
async def add_message_route(
    req: MessageRequest,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Add a user message to a conversation"""
    # Create or use existing conversation
    conversation_id = req.conversation_id

    if not conversation_id:
        # Create a new conversation if one isn't provided
        title = (
            req.title or req.message[:20]
        )  # Use the first 20 characters of the message as title
        conversation_id = await create_conversation(session, user.id, title)
        logger.info(f"Created new conversation {conversation_id} for user {user.id}")
    else:
        # Verify the conversation exists and belongs to the user
        conversation = await get_conversation(session, conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        if conversation.get("user_id") != user.id:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to add messages to this conversation",
            )

    # Create event data for the message
    user_event_data = {
        "type": "user_message",
        "content": req.message,
        "sender_id": user.id,
        "timestamp": datetime.now(UTC).isoformat(),
    }

    # Add the message
    message_id = await add_message(session, conversation_id, user_event_data)

    return MessageResponse(
        id=message_id,
        conversation_id=conversation_id,
        created_at=user_event_data["timestamp"],
        event_data=user_event_data,
    )


@router.get(
    "/conversation/{conversation_id}/messages", response_model=List[MessageResponse]
)
async def get_conversation_messages_route(
    conversation_id: str,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    limit: int = Query(
        20, ge=1, le=100, description="Maximum number of messages to return"
    ),
    offset: int = Query(
        0, ge=0, description="Number of messages to skip (for pagination)"
    ),
):
    """
    Get messages for a specific conversation with pagination support.
    Results are sorted by created_at in ascending order (oldest first).
    """
    # Verify the conversation exists and belongs to the user
    conversation = await get_conversation(session, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.get("user_id") != user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view messages for this conversation",
        )

    # Get messages
    messages = await get_conversation_messages(
        session, conversation_id, limit=limit, offset=offset
    )
    return [MessageResponse(**m) for m in messages]
