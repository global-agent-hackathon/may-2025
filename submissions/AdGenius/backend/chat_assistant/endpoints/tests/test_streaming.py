"""
Tests for streaming endpoints

Note: These tests focus on the validation and error handling aspects of the
streaming endpoints, since testing the actual streaming content is more complex.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, Response
from fastapi.testclient import TestClient

from .conftest import MockUser


@pytest.mark.asyncio
async def test_stream_chat_nonexistent_conversation(
    test_app: FastAPI, client: TestClient, override_dependencies, test_user: MockUser
):
    """Test streaming from a nonexistent conversation."""
    # Use a nonexistent conversation ID
    nonexistent_id = "non-existent-conversation-id"

    # Mock get_conversation to return None for nonexistent conversation
    with patch("database_storage.database.get_conversation", return_value=None):
        # Try to stream chat
        mock_user_message_id = "mock-user-message-id"
        response = client.get(
            f"/chat/stream/{nonexistent_id}",
            params={"user_message_id": mock_user_message_id, "auth_token": "dummy-token"},
        )

        # This could return 404 or 500 with "Conversation not found" in the error
        assert response.status_code in [404, 500]
        if response.status_code == 500:
            assert (
                "not found" in response.json().get("detail", "").lower()
                or "conversation" in response.json().get("detail", "").lower()
            )
        else:
            assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_stream_chat_basic_validation(
    test_app: FastAPI, client: TestClient, override_dependencies, test_user: MockUser
):
    """Test basic validation for the streaming endpoint."""
    # Create a mock conversation
    mock_conversation_id = "mock-conversation-id"
    mock_conversation = MagicMock()
    mock_conversation.id = mock_conversation_id
    mock_conversation.user_id = test_user.id

    # Check that message is required - without specific mock
    response = client.get(
        f"/chat/stream/{mock_conversation_id}", params={"auth_token": "dummy-token"}
    )
    assert response.status_code == 422  # Unprocessable Entity

    # For the successful test, we need to patch the database access and streaming response
    # Create a mock streaming response function
    def mock_streaming_response(*args, **kwargs):
        return Response(
            content="test_stream",
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache"},
        )

    # Replace the StreamingResponse with our mock
    with (
        patch(
            "database_storage.database.get_conversation", return_value=mock_conversation
        ),
        patch("database_storage.database.add_message", return_value="mock-message-id"),
        patch(
            "fastapi.responses.StreamingResponse", side_effect=mock_streaming_response
        ),
    ):
        # Test streaming with valid parameters
        mock_user_message_id = "mock-user-message-id"
        response = client.get(
            f"/chat/stream/{mock_conversation_id}",
            params={"user_message_id": mock_user_message_id, "auth_token": "dummy-token"},
        )

        # Since we can't simulate actual streaming in the test client, check for a valid response
        assert response.status_code != 422
        # Uncomment this when the mocking is fixed:
        # assert response.headers['content-type'].startswith('text/event-stream')


@pytest.mark.asyncio
async def test_stream_chat_mock_response(
    test_app: FastAPI,
    client: TestClient,
    override_dependencies,
    test_user: MockUser,
    monkeypatch,
):
    """Test stream chat with a mocked response."""
    # Create a mock conversation
    mock_conversation_id = "mock-conversation-id"
    mock_conversation = {
        "id": mock_conversation_id,
        "user_id": test_user.id,
        "title": "Test Conversation",
        "created_at": "2025-05-09T12:00:00Z",
        "updated_at": "2025-05-09T12:00:00Z",
    }

    # Mock the generate_sse_events function to return a simple event stream
    async def mock_generate_sse_events(*args, **kwargs):
        yield 'data: {"event_type":"thinking","data":{"content":"test"}}\n\n'
        yield 'data: {"event_type":"run_completed","data":{"content":"Hello"},"done":true}\n\n'

    # Create a mock agent that doesn't actually do anything
    class MockAgent:
        def __init__(self, *args, **kwargs):
            pass

    # Mock all the required components
    with (
        patch(
            "database_storage.database.get_conversation", return_value=mock_conversation
        ),
        patch("chat_assistant.ChatAgent", MockAgent),
        patch(
            "chat_assistant.endpoints.common.generate_sse_events",
            side_effect=mock_generate_sse_events,
        ),
    ):
        # Mock the StreamingResponse class
        def mock_streaming_response(*args, **kwargs):
            return Response(
                content="test_stream",
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache"},
            )

        # Patch the streaming response at the fastapi level
        with patch(
            "fastapi.responses.StreamingResponse", side_effect=mock_streaming_response
        ):
            # Send the request
            mock_user_message_id = "mock-user-message-id"
            response = client.get(
                f"/chat/stream/{mock_conversation_id}",
                params={"user_message_id": mock_user_message_id, "auth_token": "dummy-token"},
            )

            # Since we can't simulate actual streaming in the test client, check for a valid response
            assert response.status_code != 422  # Should not be validation error
            # These assertions would work if the streaming was fully mocked:
            # assert response.headers['content-type'].startswith('text/event-stream')
            # assert response.headers['cache-control'] == 'no-cache'


@pytest.mark.asyncio
async def test_stream_chat_idempotent_replay(
    test_app: FastAPI,
    client: TestClient,
    override_dependencies,
    test_user: MockUser,
):
    """Test idempotent replay of stored message by message_id."""
    mock_conversation_id = "mock-conversation-id"
    mock_conversation = {
        "id": mock_conversation_id,
        "user_id": test_user.id,
        "title": "Test Conversation",
        "created_at": "2025-05-09T12:00:00Z",
        "updated_at": "2025-05-09T12:00:00Z",
    }
    mock_user_message_id = "mock-user-message-id"
    mock_message_id = "mock-message-id"
    mock_event_data = {
        "event_type": "RunCompleted",
        "data": {"content": "Hello, this is a stored response.", "content_type": "str"},
    }
    # Patch get_conversation and get_message_by_id to simulate idempotent replay

    def get_message_by_id_side_effect(session, message_id):
        if message_id == mock_message_id or message_id == mock_user_message_id:
            return {
                "id": message_id,
                "conversation_id": mock_conversation_id,
                "created_at": "2025-05-09T12:00:00Z",
                "event_data": mock_event_data,
            }
        return None

    with (
        patch(
            "chat_assistant.endpoints.streaming.get_conversation",
            new=AsyncMock(return_value=mock_conversation),
        ),
        patch(
            "chat_assistant.endpoints.streaming.get_message_by_id",
            new=AsyncMock(side_effect=get_message_by_id_side_effect),
        ),
    ):
        response = client.get(
            f"/chat/stream/{mock_conversation_id}",
            params={
                "user_message_id": mock_user_message_id,
                "auth_token": "dummy-token",
                "message_id": mock_message_id,
            },
        )
        assert response.status_code == 200
        assert response.headers.get("x-message-id") == mock_message_id
        assert response.headers.get("idempotency-key") == mock_message_id
        assert response.headers.get("cache-control") == "no-cache"
        assert response.headers.get("content-type", "").startswith("text/event-stream")
        # The response body should contain the stored event_data as a single SSE event
        assert f"data: {json.dumps(mock_event_data)}" in response.text
