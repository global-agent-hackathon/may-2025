"""
Tests for message endpoints
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from sqlalchemy.future import select
from sqlalchemy import text

from utils.test_helpers import create_test_conversation_db, create_test_message_db
from .conftest import MockUser
from database_storage.repository.sqlite import ConversationTable


@pytest.mark.asyncio
async def test_add_message(
    test_app: FastAPI,
    client: TestClient,
    override_dependencies,
    test_user: MockUser,
    db_session
):
    """Test adding a message to a conversation."""
    # Verify that the conversations table exists using raw SQL
    result = await db_session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
    tables = [row[0] for row in result.fetchall()]
    assert "conversations" in tables, f"Conversations table not found. Available tables: {tables}"
    assert "messages" in tables, f"Messages table not found. Available tables: {tables}"
    
    # First create a conversation directly in the database
    conversation = await create_test_conversation_db(db_session, test_user.id, "Message Test")
    conversation_id = conversation["id"]
    
    # Verify the conversation was created in the database
    result = await db_session.execute(select(ConversationTable).where(ConversationTable.id == conversation_id))
    db_conversation = result.scalar_one_or_none()
    assert db_conversation is not None, "Conversation was not created in the database"
    assert db_conversation.id == conversation_id
    
    # Add a message
    response = client.post(
        "/chat/message",
        json={
            "conversation_id": conversation_id,
            "message": "Hello from the test!"
        }
    )
    assert response.status_code == 200
    
    # Check response content
    data = response.json()
    assert "id" in data
    assert data["conversation_id"] == conversation_id
    assert "created_at" in data
    assert "event_data" in data
    assert data["event_data"]["type"] == "user_message"
    assert data["event_data"]["content"] == "Hello from the test!"
    assert data["event_data"]["sender_id"] == test_user.id


@pytest.mark.asyncio
async def test_get_conversation_messages(
    test_app: FastAPI,
    client: TestClient,
    override_dependencies,
    test_user: MockUser,
    db_session
):
    """Test getting messages for a conversation with pagination and order."""
    # First create a conversation directly in the database
    conversation = await create_test_conversation_db(db_session, test_user.id, "Get Messages Test")
    conversation_id = conversation["id"]
    
    # Add multiple messages directly in the database
    message_texts = [f"Message {i}" for i in range(1, 31)]  # 30 messages
    for msg_text in message_texts:
        await create_test_message_db(db_session, conversation_id, msg_text)
    
    # Get messages for the conversation (default limit=20, should get 20 most recent)
    response = client.get(f"/chat/conversation/{conversation_id}/messages")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 20
    # Should be the 20 most recent messages (descending order)
    expected = list(reversed(message_texts))[:20]
    actual = [m["event_data"]["content"] for m in data]
    assert actual == expected

    # Get messages with custom limit=10
    response = client.get(f"/chat/conversation/{conversation_id}/messages?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10
    expected = list(reversed(message_texts))[:10]
    actual = [m["event_data"]["content"] for m in data]
    assert actual == expected

    # Get messages with offset=5 (should skip 5 most recent)
    response = client.get(f"/chat/conversation/{conversation_id}/messages?limit=10&offset=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10
    expected = list(reversed(message_texts))[5:15]
    actual = [m["event_data"]["content"] for m in data]
    assert actual == expected

    # Get all messages (limit=100)
    response = client.get(f"/chat/conversation/{conversation_id}/messages?limit=100")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 30
    expected = list(reversed(message_texts))
    actual = [m["event_data"]["content"] for m in data]
    assert actual == expected


@pytest.mark.asyncio
async def test_add_message_nonexistent_conversation(
    test_app: FastAPI,
    client: TestClient,
    override_dependencies,
    test_user: MockUser
):
    """Test adding a message to a nonexistent conversation."""
    # Use a nonexistent conversation ID
    nonexistent_id = "non-existent-conversation-id"
    
    # Try to add a message
    response = client.post(
        "/chat/message",
        json={
            "conversation_id": nonexistent_id,
            "message": "This should fail"
        }
    )
    
    # Should get a 404 error
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_messages_from_nonexistent_conversation(
    test_app: FastAPI,
    client: TestClient,
    override_dependencies,
    test_user: MockUser
):
    """Test getting messages from a nonexistent conversation."""
    # Use a nonexistent conversation ID
    nonexistent_id = "non-existent-conversation-id"
    
    # Try to get messages
    response = client.get(f"/chat/conversation/{nonexistent_id}/messages")
    
    # Should get a 404 error
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_add_message_create_conversation(
    test_app: FastAPI,
    client: TestClient,
    override_dependencies,
    test_user: MockUser,
    db_session
):
    """Test adding a message without an existing conversation (should create one)."""
    # Directly add a message without creating a conversation first
    response = client.post(
        "/chat/message",
        json={
            "conversation_id": None,  # Explicitly set to None to test auto-creation
            "message": "Hello without conversation!",
            "title": "Auto-created conversation"
        }
    )
    
    # Should successfully create conversation and add message
    assert response.status_code == 200
    
    # Check response content
    data = response.json()
    assert "id" in data
    assert "conversation_id" in data
    conversation_id = data["conversation_id"]
    assert conversation_id is not None  # Should have a valid conversation ID
    assert "created_at" in data
    assert "event_data" in data
    assert data["event_data"]["type"] == "user_message"
    assert data["event_data"]["content"] == "Hello without conversation!"
    assert data["event_data"]["sender_id"] == test_user.id
    
    # Since we've verified the message was added with the correct conversation_id,
    # we can be confident the conversation was created properly
    
    # For extra validation, let's try to add another message to the same conversation
    second_response = client.post(
        "/chat/message",
        json={
            "conversation_id": conversation_id,
            "message": "Second message to the auto-created conversation"
        }
    )
    
    # Should succeed if the conversation exists
    assert second_response.status_code == 200
    second_data = second_response.json()
    assert second_data["conversation_id"] == conversation_id 