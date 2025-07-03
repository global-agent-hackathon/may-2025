"""
Common imports, models, and utilities for chat endpoints
"""

import json
import time
from collections import OrderedDict
from typing import Any, AsyncGenerator, Dict, Optional, Tuple

from agno.run.response import RunEvent
from fastapi import Depends, HTTPException, Query
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

# Import the chat agent from the parent package
from chat_assistant import ChatAgent

# Import database utilities from the parent package
from database_storage import (
    add_message,
    get_session,
    init_chat_db,
)

# Import user authentication utilities
from google_oauth import get_current_user, get_user_by_email
from utils import config, get_logger

# Cache for tracking processed message IDs to ensure idempotency
# Using OrderedDict to maintain insertion order for easy removal of oldest items
# Format: {message_id: (timestamp, response_chunks)}
MESSAGE_CACHE_SIZE = 1000  # Maximum number of messages to cache
MESSAGE_CACHE_TTL = 3600  # Time-to-live in seconds (1 hour)
message_cache: OrderedDict[str, Tuple[float, list]] = OrderedDict()

# Configure logging
logger = get_logger(__name__)


# Models
class MessageRequest(BaseModel):
    """Request model for sending a message"""

    conversation_id: Optional[str] = None
    message: str
    title: Optional[str] = None  # Optional title for creating a new conversation


class ConversationResponse(BaseModel):
    """Response model for conversation data"""

    id: str
    title: str
    created_at: str
    updated_at: str


class MessageResponse(BaseModel):
    """Response model for message data"""

    id: str
    conversation_id: str
    created_at: str
    event_data: Dict[str, Any]


# Dependency to get current user from auth_token query parameter
async def get_current_user_from_query_token(
    auth_token: str = Query(...), db: AsyncSession = Depends(get_session)
):
    if not auth_token:
        logger.error("Missing auth_token in query parameter")
        raise HTTPException(status_code=401, detail="Missing auth_token")
    try:
        payload = jwt.decode(
            auth_token, config.secret_key, algorithms=[config.algorithm]
        )
        user_email = payload.get("sub")
        if not user_email:
            logger.error("Invalid token: missing subject")
            raise HTTPException(
                status_code=401, detail="Invalid token: missing subject"
            )
        user = await get_user_by_email(session=db, email=user_email)
        if not user:
            logger.error(f"User not found for email: {user_email}")
            raise HTTPException(status_code=401, detail="User not found")
        logger.info(f"Token auth successful for streaming: user {user.email}")
        return user
    except JWTError as e:
        logger.error(f"Invalid token: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


# Helper function to clean expired cache entries
def clean_message_cache():
    """Remove expired entries from the message cache"""
    current_time = time.time()
    expired_keys = []

    # Find expired entries
    for key, (timestamp, _) in message_cache.items():
        if current_time - timestamp > MESSAGE_CACHE_TTL:
            expired_keys.append(key)

    # Remove expired entries
    for key in expired_keys:
        message_cache.pop(key, None)

    # If still over size limit, remove oldest entries
    while len(message_cache) > MESSAGE_CACHE_SIZE:
        message_cache.popitem(last=False)  # Remove oldest item (first inserted)


# Helper function to generate SSE events
async def generate_sse_events(
    agent: ChatAgent,
    message: str,
    session: AsyncSession,
    message_id: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    """Generate Server-Sent Events for streaming chat responses

    Args:
        agent: The chat agent instance
        message: The message to process
        session: Database session
        message_id: Unique identifier for this message, used for idempotency
    """
    # Clean expired cache entries
    if message_id:
        clean_message_cache()

    # Check if this message has already been processed
    if message_id and message_id in message_cache:
        logger.info(
            f"Message {message_id} already processed, returning cached response"
        )
        _, cached_chunks = message_cache[message_id]

        # Move to end to mark as recently used
        message_cache.move_to_end(message_id)

        # Return cached chunks
        for chunk in cached_chunks:
            yield f"data: {chunk}\n\n"
        return

    # Initialize empty list for storing chunks and final response
    response_chunks = []

    try:
        # Add to cache if message_id provided
        if message_id is not None:
            message_cache[message_id] = (time.time(), response_chunks)

        # Get the message stream from the agent - disable automatic message storage
        # when using message_id (we'll store it ourselves with the message ID)
        message_stream = agent.process_message(message)

        # Process the stream
        async for chunk in message_stream:
            if chunk:
                # Parse the JSON to access the event data
                event_data = json.loads(chunk)
                # event_type = event_data.get("event_type")

                # Check if this is the final response that should be stored
                if event_data.get("done", False):
                    await add_message(
                        session, agent.conversation_id, event_data, message_id
                    )

                # Store chunk in cache if using message_id
                if message_id:
                    response_chunks.append(chunk)

                # Format as SSE and send to client
                yield f"data: {chunk}\n\n"

    except Exception as e:
        # Log the error
        logger.error(
            f"Error in SSE generator for message {message_id}: {str(e)}", exc_info=True
        )
        # Handle exceptions
        error_chunk = json.dumps(
            {
                "event_type": RunEvent.run_error.value,
                "data": {
                    "error_message": f"Error: {str(e)}",
                    "details": "Critical error during SSE stream processing.",
                },
                "done": True,
            }
        )

        # Store error in cache if using message_id
        if message_id:
            response_chunks.append(error_chunk)

        # Return error as SSE
        yield f"data: {error_chunk}\n\n"

        # If empty response due to early error, remove from cache
        if message_id and not response_chunks:
            message_cache.pop(message_id, None)


# Initialize the chat database on startup
async def setup_chat_db():
    """Initialize chat database tables"""
    await init_chat_db()


# Re-export get_current_user from google_oauth so other modules can import it from here
__all__ = ["get_current_user", "get_current_user_from_query_token", "get_session"]
