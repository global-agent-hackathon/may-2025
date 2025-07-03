"""
Test helper utilities for database storage tests
"""

import json
import uuid
from datetime import UTC, datetime
from typing import Any, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from database_storage.repository.sqlite import ConversationTable, MessageTable


async def create_test_conversation_db(
    session: AsyncSession,
    user_id: str = "test-user-id",
    title: str = "Test Conversation",
) -> Dict[str, Any]:
    """
    Helper to create a test conversation directly in the database.

    Args:
        session: SQLAlchemy async session
        user_id: User ID for the conversation
        title: The conversation title

    Returns:
        The created conversation data as a dictionary
    """
    now = datetime.now(UTC)
    conversation_id = str(uuid.uuid4())

    conversation = ConversationTable(
        id=conversation_id,
        user_id=user_id,
        title=title,
        created_at=now,
        updated_at=now,
    )
    session.add(conversation)
    await session.commit()

    # Return in the same format as the API response
    return {
        "id": conversation_id,
        "user_id": user_id,
        "title": title,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }


async def create_test_message_db(
    session: AsyncSession, conversation_id: str, content: str = "Test message content"
) -> Dict[str, Any]:
    """
    Helper to create a test message directly in the database.

    Args:
        session: SQLAlchemy async session
        conversation_id: ID of the conversation
        content: The message content

    Returns:
        The created message data as a dictionary
    """
    now = datetime.now(UTC)
    message_id = str(uuid.uuid4())

    event_data = {
        "content": content,
        "type": "user_message",
        "sender_id": "test-user-id",
    }

    message = MessageTable(
        id=message_id,
        conversation_id=conversation_id,
        data=json.dumps(event_data),
        created_at=now,
    )
    session.add(message)
    await session.commit()

    # Also update the conversation timestamp
    result = await session.get(ConversationTable, conversation_id)
    if result:
        result.updated_at = now  # type: ignore
        await session.commit()

    # Return in the same format as the API response
    return {
        "id": message_id,
        "conversation_id": conversation_id,
        "created_at": now.isoformat(),
        "event_data": event_data,
    }


async def create_multiple_test_conversations_db(
    session: AsyncSession,
    user_id: str = "test-user-id",
    count: int = 5,
    title_prefix: str = "Test Conversation",
) -> List[Dict[str, Any]]:
    """
    Helper to create multiple test conversations directly in the database.

    Args:
        session: SQLAlchemy async session
        user_id: User ID for the conversations
        count: Number of conversations to create
        title_prefix: Prefix for the conversation titles

    Returns:
        List of created conversation data dictionaries
    """
    conversations = []

    for i in range(count):
        conversation = await create_test_conversation_db(
            session=session, user_id=user_id, title=f"{title_prefix} {i}"
        )
        conversations.append(conversation)

    return conversations
