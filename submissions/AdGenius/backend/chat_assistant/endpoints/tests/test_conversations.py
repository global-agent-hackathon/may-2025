"""
Tests for conversation endpoints
"""

import time
from datetime import datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from utils.test_helpers import (
    assert_api_response,
    create_multiple_test_conversations_db,
    create_test_conversation_db,
)

from .conftest import MockUser


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_conversations(
    test_app: FastAPI,
    client: TestClient,
    override_dependencies,
    test_user: MockUser,
    db_session,
):
    """Test listing user conversations."""
    # Create multiple conversations directly in the database
    await create_test_conversation_db(db_session, test_user.id, "Conversation 1")
    await create_test_conversation_db(db_session, test_user.id, "Conversation 2")

    # List conversations
    response = client.get("/chat/conversations")

    # Check response using helper function
    data = assert_api_response(response)

    # Check the conversations are in the list
    titles = [conv["title"] for conv in data]
    assert "Conversation 1" in titles
    assert "Conversation 2" in titles


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_conversations_with_pagination(
    test_app: FastAPI,
    client: TestClient,
    override_dependencies,
    test_user: MockUser,
    db_session,
):
    """Test listing user conversations with pagination."""
    # Create more than the default limit (20) conversations directly in the database
    await create_multiple_test_conversations_db(
        db_session, test_user.id, 25, "Pagination Test"
    )

    # Get first page (default limit is 20)
    response = client.get("/chat/conversations")
    data = assert_api_response(response)

    # Should get 20 items (default limit)
    assert len(data) == 20

    # Get second page
    response = client.get("/chat/conversations?offset=20")
    data = assert_api_response(response)

    # Should get remaining items (considering the test fixture adds one conversation)
    assert len(data) == 6

    # Test custom limit
    response = client.get("/chat/conversations?limit=10")
    data = assert_api_response(response)
    assert len(data) == 10


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_conversations_sorting(
    test_app: FastAPI,
    client: TestClient,
    override_dependencies,
    test_user: MockUser,
    db_session,
):
    """Test that conversations are sorted by updated_at in descending order."""
    # Create conversations with controlled timestamps
    await create_test_conversation_db(db_session, test_user.id, "Oldest Conversation")
    time.sleep(0.1)  # Ensure different timestamps
    await create_test_conversation_db(db_session, test_user.id, "Middle Conversation")
    time.sleep(0.1)  # Ensure different timestamps
    await create_test_conversation_db(db_session, test_user.id, "Newest Conversation")

    # Get conversations (should be sorted by updated_at desc)
    response = client.get("/chat/conversations")
    data = assert_api_response(response)

    # First should be the newest, and so on
    assert data[0]["title"] == "Newest Conversation"
    assert data[1]["title"] == "Middle Conversation"
    assert data[2]["title"] == "Oldest Conversation"

    # Verify the timestamps are in the correct order
    assert datetime.fromisoformat(data[0]["updated_at"]) > datetime.fromisoformat(
        data[1]["updated_at"]
    )
    assert datetime.fromisoformat(data[1]["updated_at"]) > datetime.fromisoformat(
        data[2]["updated_at"]
    )
    assert datetime.fromisoformat(data[0]["updated_at"]) > datetime.fromisoformat(
        data[1]["updated_at"]
    )
    assert datetime.fromisoformat(data[1]["updated_at"]) > datetime.fromisoformat(
        data[2]["updated_at"]
    )
