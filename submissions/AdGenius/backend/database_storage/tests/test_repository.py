"""
Tests for the database storage repository implementation
"""

from datetime import UTC, datetime

import pytest

from database_storage import (
    add_message,
    create_conversation,
    delete_conversation,
    get_conversation,
    get_conversation_messages,
    get_user_conversations,
)
from database_storage.repository.sqlite import (
    CONVERSATION_NAMESPACE,
    MESSAGE_NAMESPACE,
)

# Register pytest_asyncio plugin
pytest_plugins = ["pytest_asyncio"]

DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# Use async_session fixture from conftest.py


@pytest.mark.asyncio
async def test_conversation_crud(async_session):
    user_id = "test-user"
    # Create
    conversation_id = await create_conversation(async_session, user_id, "Test Conversation")
    assert conversation_id
    # Get
    conversation = await get_conversation(async_session, conversation_id)
    assert conversation is not None
    assert conversation["user_id"] == user_id
    assert conversation["title"] == "Test Conversation"
    # List
    conversations = await get_user_conversations(async_session, user_id)
    assert len(conversations) == 1
    # Delete
    result = await delete_conversation(async_session, conversation_id)
    assert result is True
    conversations = await get_user_conversations(async_session, user_id)
    assert len(conversations) == 0


@pytest.mark.asyncio
async def test_message_crud(async_session):
    # Skip the connection validation since we know the tables were created properly
    # in the session fixture which called Base.metadata.create_all

    # Now proceed with the test
    user_id = "test-user"
    conversation_id = await create_conversation(async_session, user_id, "Msg Conversation")

    # Create event data for the message
    event_data = {
        "type": "user_message",
        "content": "Hello world!",
        "sender_id": user_id,
        "timestamp": datetime.now(UTC).isoformat(),
    }

    # Add message with event data
    message_id = await add_message(async_session, conversation_id, event_data)
    assert message_id

    # Get messages
    messages = await get_conversation_messages(async_session, conversation_id)
    assert len(messages) == 1

    # Check the structure of the returned message
    message = messages[0]
    assert "id" in message
    assert "conversation_id" in message
    assert "created_at" in message
    assert "event_data" in message

    # Verify the content is inside event_data
    assert message["event_data"]["type"] == "user_message"
    assert message["event_data"]["content"] == "Hello world!"
    assert message["event_data"]["sender_id"] == user_id

    # Delete conversation (should cascade delete messages)
    await delete_conversation(async_session, conversation_id)
    messages = await get_conversation_messages(async_session, conversation_id)
    assert len(messages) == 0


@pytest.mark.asyncio
async def test_uuid_generation_consistency():
    """Test that UUID5 generation is deterministic for the same inputs"""
    import uuid

    # Test conversation ID generation
    user_id = "test-user"
    timestamp = "1234567890.123456"  # Use fixed timestamp for testing

    # Generate two UUIDs with the same input
    conv_id1 = str(uuid.uuid5(CONVERSATION_NAMESPACE, user_id + timestamp))
    conv_id2 = str(uuid.uuid5(CONVERSATION_NAMESPACE, user_id + timestamp))

    # They should be identical
    assert conv_id1 == conv_id2

    # Test message ID generation
    conversation_id = "test-conversation-id"

    # Generate two UUIDs with the same input
    msg_id1 = str(uuid.uuid5(MESSAGE_NAMESPACE, conversation_id + timestamp))
    msg_id2 = str(uuid.uuid5(MESSAGE_NAMESPACE, conversation_id + timestamp))

    # They should be identical
    assert msg_id1 == msg_id2

    # But conversation and message IDs should be different
    assert conv_id1 != msg_id1


@pytest.mark.asyncio
async def test_complex_event_data_storage(async_session):
    """Test that complex JSON data can be stored and retrieved correctly"""
    user_id = "test-user"
    conversation_id = await create_conversation(async_session, user_id, "Complex Data Test")

    # Create a complex event data structure with nested objects and arrays
    complex_event_data = {
        "event": "RunCompleted",
        "content": "The current time is May 8, 2025, 10:00 PM.",
        "content_type": "str",
        "reasoning_content": "## Checking the current time\nThe user is asking for the current time.",
        "model": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        "run_id": "21e3ee7d-16e8-4bd9-963e-036fa2262e83",
        "agent_id": "95b90c33-98ce-4e9d-b43b-170372a70908",
        "session_id": "conv-2025-05-08T21:58:53.129484-00d8ed30-590f-46a2-8a5b-a415de3b7e4f",
        "tools": [
            {
                "content": "Step 1:\nTitle: Checking the current time\nReasoning: The user is asking for the current time.",
                "tool_call_id": "toolu_bdrk_01WpFMRvnQX4XaduBr8eQHAj",
                "tool_name": "think",
                "tool_args": {
                    "title": "Checking the current time",
                    "thought": "The user is asking for the current time.",
                    "confidence": 1.0,
                    "action": "provide the current time to the user",
                },
                "tool_call_error": False,
                "metrics": {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "audio_tokens": 0,
                    "time": 0.0027979169972240925,
                },
                "created_at": 1746712846,
            }
        ],
        "created_at": 1746712859,
    }

    # Add message with complex event data
    message_id = await add_message(async_session, conversation_id, complex_event_data)
    assert message_id

    # Get messages
    messages = await get_conversation_messages(async_session, conversation_id)
    assert len(messages) == 1

    # Verify all complex data was preserved
    message = messages[0]
    event_data = message["event_data"]

    # Check top-level fields
    assert event_data["event"] == "RunCompleted"
    assert event_data["content"] == "The current time is May 8, 2025, 10:00 PM."
    assert event_data["model"] == "us.anthropic.claude-3-7-sonnet-20250219-v1:0"

    # Check nested array
    assert len(event_data["tools"]) == 1
    tool = event_data["tools"][0]
    assert tool["tool_name"] == "think"

    # Check deeply nested object
    assert tool["tool_args"]["title"] == "Checking the current time"
    assert tool["tool_args"]["confidence"] == 1.0

    # Check boolean values are preserved
    assert tool["tool_call_error"] is False

    # Check nested metrics
    assert tool["metrics"]["time"] == 0.0027979169972240925
