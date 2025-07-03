"""
Database utilities for the Database Storage package

This module serves as a facade for the repository implementation, providing
backward compatibility with the previous database interface.
"""

import logging
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.sql import text

from database_storage.repository.interfaces import ChatRepository
from database_storage.repository.sqlite import (
    Base,
    SQLAlchemyChatRepository,
)
from utils.config import config

# Configure logging
logger = logging.getLogger(__name__)

# Create async engine and session
engine = create_async_engine(config.database_url, echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


# Dependency for FastAPI
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


def get_repository(session: AsyncSession) -> ChatRepository:
    return SQLAlchemyChatRepository(session)


# Database initialization
async def init_chat_db():
    """Initialize the SQLAlchemy database tables for chat functionality.

    This function creates the necessary tables if they don't exist.
    """
    try:
        logger.info("Initializing chat database schema...")

        # Create tables directly with the engine, similar to google_oauth approach
        async with engine.begin() as conn:
            # Create tables without dropping existing ones (the default behavior)
            await conn.run_sync(Base.metadata.create_all)

            # Verify tables were created (useful for debugging)
            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            )
            tables = [row[0] for row in result.fetchall()]
            logger.info(f"Database tables: {tables}")

            # Verify essential tables exist
            for table in ["conversations", "messages"]:
                if table not in tables:
                    logger.error(f"Table '{table}' was not created properly!")
                    raise Exception(f"Failed to create required table: {table}")

        logger.info("Chat database schema initialization complete")
    except Exception as e:
        logger.error(f"Error initializing database schema: {str(e)}", exc_info=True)
        raise


# Conversation operations
async def create_conversation(
    session: AsyncSession, user_id: str, title: Optional[str] = None
) -> str:
    repo = SQLAlchemyChatRepository(session)
    return await repo.conversations.create(user_id, title)


async def get_conversation(
    session: AsyncSession, conversation_id: str
) -> Optional[Dict[str, Any]]:
    repo = SQLAlchemyChatRepository(session)
    return await repo.conversations.get(conversation_id)


async def get_user_conversations(
    session: AsyncSession, user_id: str, limit: int = 20, offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Get all conversations for a user with pagination support.

    Args:
        session: SQLAlchemy async session
        user_id: User ID to filter conversations by
        limit: Maximum number of conversations to return (default: 20)
        offset: Number of conversations to skip (for pagination)

    Returns:
        List of conversations sorted by updated_at in descending order
    """
    repo = SQLAlchemyChatRepository(session)
    return await repo.conversations.get_by_user(user_id, limit=limit, offset=offset)


async def delete_conversation(session: AsyncSession, conversation_id: str) -> bool:
    repo = SQLAlchemyChatRepository(session)
    await repo.messages.delete_by_conversation(conversation_id)
    return await repo.conversations.delete(conversation_id)


# Message operations
async def add_message(
    session: AsyncSession,
    conversation_id: str,
    event_data: Dict[str, Any],
    message_id: Optional[str] = None,
) -> str:
    repo = SQLAlchemyChatRepository(session)
    return await repo.messages.add(conversation_id, event_data, message_id)


async def get_message_by_id(
    session: AsyncSession, message_id: str
) -> Optional[Dict[str, Any]]:
    repo = SQLAlchemyChatRepository(session)
    return await repo.messages.get_message_by_id(message_id)


async def get_conversation_messages(
    session: AsyncSession, conversation_id: str, limit: int = 20, offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Get messages for a conversation, ordered by created_at descending (most recent first).
    """
    repo = SQLAlchemyChatRepository(session)
    return await repo.messages.get_by_conversation(
        conversation_id, limit=limit, offset=offset
    )


# Draft Campaign operations


class DraftCampaignTypes(str, Enum):
    """Enum for draft campaign types"""

    REQUIREMENTS = "requirements"
    AD_COPY = "ad_copy"
    AD_IMAGE = "ad_image"
    PUBLISHED_CAMPAIGN = "published_campaign"

async def create_draft_campaign(
    session: AsyncSession,
    type: DraftCampaignTypes,
    data: Dict[str, Any],
    conversation_id: str,
) -> str:
    """Create a new draft campaign"""
    repo = SQLAlchemyChatRepository(session)
    return await repo.draft_campaigns.create(type.value, data, conversation_id)


async def upsert_draft_campaign(
    session: AsyncSession,
    type: DraftCampaignTypes,
    data: Dict[str, Any],
    conversation_id: str,
) -> Tuple[str, bool]:
    """
    Create or update a draft campaign based on conversation_id and type.

    Args:
        session: SQLAlchemy async session
        type: Type of the draft campaign
        data: Draft campaign data
        conversation_id: ID of the conversation

    Returns:
        Tuple of (draft_id, is_new) where is_new is True if a new draft was created
    """
    repo = SQLAlchemyChatRepository(session)
    return await repo.draft_campaigns.upsert(type.value, data, conversation_id)


async def get_draft_campaign(
    session: AsyncSession,
    draft_id: str,
) -> Optional[Dict[str, Any]]:
    """Get a draft campaign by ID"""
    repo = SQLAlchemyChatRepository(session)
    return await repo.draft_campaigns.get(draft_id)


async def get_conversation_draft_campaigns(
    session: AsyncSession,
    conversation_id: str,
    type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Get draft campaigns for a conversation"""
    repo = SQLAlchemyChatRepository(session)
    return await repo.draft_campaigns.get_by_conversation(conversation_id, type)


async def update_draft_campaign(
    session: AsyncSession,
    draft_id: str,
    data: Dict[str, Any],
) -> bool:
    """Update a draft campaign"""
    repo = SQLAlchemyChatRepository(session)
    return await repo.draft_campaigns.update(draft_id, data)


async def delete_draft_campaign(
    session: AsyncSession,
    draft_id: str,
) -> bool:
    """Delete a draft campaign"""
    repo = SQLAlchemyChatRepository(session)
    return await repo.draft_campaigns.delete(draft_id)


# Campaign operations
async def create_campaign(
    session: AsyncSession,
    conversation_id: str,
    campaign_name: str,
    product_name: str,
    product_url: str,
    start_date: str,
    image_url: Optional[str] = None,
    description: Optional[str] = None,
    budget: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None,
    publisher_id: Optional[str] = None,
    publisher_data: Optional[Dict[str, Any]] = None,
) -> str:
    """Create a new campaign"""
    repo = SQLAlchemyChatRepository(session)
    return await repo.campaigns.create(
        conversation_id=conversation_id,
        campaign_name=campaign_name,
        product_name=product_name,
        product_url=product_url,
        start_date=start_date,
        image_url=image_url,
        description=description,
        budget=budget,
        end_date=end_date,
        status=status,
        publisher_id=publisher_id,
        publisher_data=publisher_data,
    )


async def get_campaign(
    session: AsyncSession, campaign_id: str
) -> Optional[Dict[str, Any]]:
    """Get a campaign by ID"""
    repo = SQLAlchemyChatRepository(session)
    return await repo.campaigns.get(campaign_id)


async def get_conversation_campaigns(
    session: AsyncSession, conversation_id: str
) -> List[Dict[str, Any]]:
    """Get campaigns for a conversation"""
    repo = SQLAlchemyChatRepository(session)
    return await repo.campaigns.get_by_conversation(conversation_id)


async def update_campaign(
    session: AsyncSession,
    campaign_id: str,
    **kwargs
) -> bool:
    """Update a campaign with new values"""
    repo = SQLAlchemyChatRepository(session)
    return await repo.campaigns.update(campaign_id, **kwargs)


async def delete_campaign(session: AsyncSession, campaign_id: str) -> bool:
    """Delete a campaign"""
    repo = SQLAlchemyChatRepository(session)
    return await repo.campaigns.delete(campaign_id)


async def update_campaign_publisher_data(
    session: AsyncSession,
    campaign_id: str,
    publisher_id: str,
    publisher_data: Dict[str, Any],
) -> bool:
    """Update a campaign with data from the ad publisher API"""
    repo = SQLAlchemyChatRepository(session)
    return await repo.campaigns.update_publisher_data(
        campaign_id, publisher_id, publisher_data
    )
