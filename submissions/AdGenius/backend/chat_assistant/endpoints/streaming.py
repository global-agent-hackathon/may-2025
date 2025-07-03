"""
Streaming chat endpoints

This module handles streaming chat functionality:
- Stream chat responses in real-time using Server-Sent Events (SSE)
 - Supports idempotent requests via message_id parameter
 - Handles duplicate request detection and processing
 - Uses message_id for database-level idempotency
"""

import hashlib
import time
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

# Import database operations
from database_storage import get_conversation, get_message_by_id

# Import common utilities
from .common import (
    ChatAgent,
    generate_sse_events,
    get_current_user_from_query_token,
    get_session,
    logger,
)

# Create router without prefix (it will be added by the parent router)
router = APIRouter()


@router.get("/stream/{conversation_id}")
async def stream_chat(
    conversation_id: str,
    user_message_id: str,
    message_id: Optional[str] = None,
    idempotency_key: Optional[str] = Header(None),
    current_user=Depends(get_current_user_from_query_token),
    session: AsyncSession = Depends(get_session),
):
    """Stream the chat response using Server-Sent Events with token in query parameter

    This endpoint supports idempotent requests using either a message_id query parameter
    or an Idempotency-Key header. If a request with the same ID is received multiple times,
    only the first one will be processed and subsequent ones will receive the same response.

    The message_id is used directly as the message identifier in the database, ensuring true
    idempotency at both the API and database levels. This means that even if the
    in-memory cache is cleared, a duplicate request with the same ID will not create
    a duplicate database entry.

    Args:
        conversation_id: The ID of the conversation
        user_message_id: Use user_message_id to get Message to send to the chat agent
        message_id: Optional unique ID for idempotent requests. If not provided,
                   a hash of the conversation_id and message will be used.
        idempotency_key: Optional header for idempotent requests (alternative to message_id)
    """
    try:
        # Verify the conversation exists and belongs to the user
        conversation = await get_conversation(session, conversation_id)
        if not conversation:
            logger.error(f"Conversation not found: {conversation_id}")
            raise HTTPException(status_code=404, detail="Conversation not found")

        if conversation.get("user_id") != current_user.id:
            logger.error(
                f"Conversation {conversation_id} belongs to user {conversation.get('user_id')}, not {current_user.id}"
            )
            raise HTTPException(
                status_code=403, detail="You don't have access to this conversation"
            )

        # Use idempotency_key header if provided and message_id not set
        if not message_id and idempotency_key:
            message_id = idempotency_key

        # Generate message_id if still not provided
        if not message_id:
            # Create a hash of the conversation_id and message for idempotency
            timestamp = int(time.time())
            content_to_hash = (
                f"{conversation_id}:{user_message_id}:{current_user.id}:{timestamp}"
            )
            message_id = hashlib.md5(content_to_hash.encode()).hexdigest()

        logger.info(f"Processing stream request with message_id: {message_id}")

        # Check for existing message by message_id
        if message_id:
            existing_message = await get_message_by_id(session, message_id)
            if existing_message:

                def replay_stored_message():
                    import json

                    yield f"data: {json.dumps(existing_message['event_data'])}\n\n"

                return StreamingResponse(
                    replay_stored_message(),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "X-Message-ID": message_id,
                        "Idempotency-Key": message_id,
                    },
                )

        # Initialize chat agent
        agent = ChatAgent(
            session=session, conversation_id=conversation_id, user_id=current_user.id
        )

        # Get the previous user messages from database
        message = await get_message_by_id(session, user_message_id)
        if not message:
            logger.error(f"Message not found: {user_message_id}")
            raise HTTPException(status_code=404, detail="Message not found")
        content = message.get("event_data", {}).get("content")
        if content is None:
            logger.error(f"event_data or content missing in message: {user_message_id}")
            raise HTTPException(
                status_code=422, detail="Message event_data or content missing"
            )

        # Return a streaming response using the SSE event generator
        return StreamingResponse(
            generate_sse_events(agent, content, session, message_id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Message-ID": message_id,
                "Idempotency-Key": message_id,
            },
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error and convert to HTTP exception
        logger.error(f"Stream error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Stream error: {str(e)}")
