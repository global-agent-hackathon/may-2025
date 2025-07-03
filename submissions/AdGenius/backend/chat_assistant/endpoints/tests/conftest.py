"""
Pytest fixtures for endpoint tests
"""

import json
import logging
import os
import sqlite3
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, AsyncGenerator, Dict, Optional

import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from chat_assistant.endpoints import chat_router
from database_storage import get_session
from database_storage.repository.sqlite import Base, ConversationTable, MessageTable
from utils.config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use a file-based SQLite database for tests with direct URI
TEST_DB_FILE = "test_chat_assistant.db"
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_FILE}"

# Create a single engine instance for all tests
engine = create_async_engine(
    TEST_DATABASE_URL, echo=True, connect_args={"check_same_thread": False}
)

# Create session factory
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


# Mock User class
class MockUser:
    def __init__(self, id: str, email: str, name: str):
        self.id = id
        self.email = email
        self.name = name


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    """Create database tables once for the entire test session"""
    logger.info("Creating database tables for tests")

    # Delete test database if it exists
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)

    # Enable foreign keys in SQLite directly
    conn = sqlite3.connect(TEST_DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.commit()
    conn.close()

    # Create all tables
    async with engine.begin() as conn:
        # Enable foreign keys
        await conn.execute(text("PRAGMA foreign_keys = ON"))

        # Drop all tables first to ensure a clean start
        await conn.run_sync(Base.metadata.drop_all)

        # Create all tables using the same approach as in the actual application
        await conn.run_sync(Base.metadata.create_all)

    # Verify tables were created with raw SQL for better diagnostics
    async with engine.begin() as conn:
        result = await conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table'")
        )
        tables = [row[0] for row in result.fetchall()]
        logger.info(f"Created tables: {tables}")

        # Critical verification
        if "conversations" not in tables:
            logger.error("Conversations table was not created!")
            raise Exception("Failed to create conversations table")
        if "messages" not in tables:
            logger.error("Messages table was not created!")
            raise Exception("Failed to create messages table")

    logger.info("Database tables created successfully")

    # Return engine for use in tests
    yield engine

    # Close engine at the end of the session
    await engine.dispose()

    # Delete the test database
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)

    logger.info("Test database engine disposed")


@pytest_asyncio.fixture
async def setup_test_data():
    """Seed the database with test data before each test"""
    logger.info("Setting up test data")

    async with async_session_maker() as session:
        # Clear existing data
        async with session.begin():
            for table in reversed(Base.metadata.sorted_tables):
                await session.execute(text(f"DELETE FROM {table.name}"))

            # Seed test data
            now = datetime.now(UTC)

            # Create test conversation
            test_conversation = ConversationTable(
                id="test-conversation-id",
                user_id="test-user-id",
                title="Test Conversation",
                created_at=now,
                updated_at=now,
            )
            session.add(test_conversation)

            # Create test message
            test_message = MessageTable(
                id="test-message-id",
                conversation_id="test-conversation-id",
                data=json.dumps({"content": "Test message content"}),
                created_at=now,
            )
            session.add(test_message)

    logger.info("Test data setup complete")
    yield


@pytest_asyncio.fixture
async def db_session(
    setup_database, setup_test_data
) -> AsyncGenerator[AsyncSession, None]:
    """Create a session for a test"""
    # Create a fresh session for each test
    async with async_session_maker() as session:
        # Enable foreign keys
        await session.execute(text("PRAGMA foreign_keys = ON"))
        yield session


@pytest.fixture
def test_app(db_session: AsyncSession) -> FastAPI:
    """Create a FastAPI test application with a test database session"""
    app = FastAPI()

    # Add the chat router to the app
    app.include_router(chat_router)

    # Override the get_session dependency
    async def override_get_session():
        yield db_session

    # Replace the dependency
    app.dependency_overrides[get_session] = override_get_session

    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    """Create a test client for the FastAPI app"""
    return TestClient(test_app)


@pytest.fixture
def test_user() -> MockUser:
    """Create a test user"""
    return MockUser(id="test-user-id", email="test@example.com", name="Test User")


@pytest.fixture
def access_token(test_user: MockUser) -> str:
    """Create a JWT token for the test user"""
    # Define token data
    expire = datetime.now(UTC) + timedelta(minutes=15)
    data = {
        "sub": test_user.email,
        "exp": expire,
    }

    # Create the JWT token
    token = jwt.encode(data, config.secret_key, algorithm=config.algorithm)

    return token


@pytest.fixture
def auth_headers(access_token: str) -> Dict[str, str]:
    """Create authorization headers with the access token"""
    return {"Authorization": f"Bearer {access_token}"}


# Override dependencies
@pytest.fixture
def override_dependencies(test_app: FastAPI, test_user: MockUser):
    """Override dependencies for testing"""

    # Override get_current_user
    async def mock_get_current_user():
        return test_user

    # Override get_current_user_from_query_token
    async def mock_get_current_user_from_query_token(auth_token: str | None = None):
        return test_user

    # Apply overrides
    from chat_assistant.endpoints.common import (
        get_current_user,
        get_current_user_from_query_token,
    )

    test_app.dependency_overrides[get_current_user] = mock_get_current_user
    test_app.dependency_overrides[get_current_user_from_query_token] = (
        mock_get_current_user_from_query_token
    )

    yield

    # Remove overrides
    test_app.dependency_overrides = {}


# Test data helper functions
def create_test_conversation_data(
    user_id: str = "test-user-id",
    title: str = "Test Conversation",
    conversation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Create test conversation data"""
    now = datetime.now(UTC)
    if conversation_id is None:
        conversation_id = str(uuid.uuid4())

    return {
        "id": conversation_id,
        "user_id": user_id,
        "title": title,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }


def create_test_message_data(
    conversation_id: str,
    content: str = "Test message content",
    message_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Create test message data"""
    now = datetime.now(UTC)
    if message_id is None:
        message_id = str(uuid.uuid4())

    return {
        "id": message_id,
        "conversation_id": conversation_id,
        "created_at": now.isoformat(),
        "event_data": {"content": content},
    }
