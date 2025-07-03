"""
SQLite implementation of the database repositories

This module provides a SQLite-based implementation of the repository interfaces.
"""

import json
import logging
import uuid
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import declarative_base, relationship

from database_storage.repository.interfaces import (
    CampaignRepository,
    ChatRepository,
    ConversationRepository,
    DraftCampaignRepository,
    MessageRepository,
)

# Configure logging
logger = logging.getLogger(__name__)

# Use recommended SQLAlchemy 2.0 approach for declarative base
Base = declarative_base()

# Add a UUID namespace constant for conversation IDs
CONVERSATION_NAMESPACE = uuid.UUID(
    "24cfc617-be62-4c65-b36a-5a9ce8d7c616"
)  # Random UUID for conversation namespace

# Add another UUID namespace constant for message IDs
MESSAGE_NAMESPACE = uuid.UUID(
    "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
)  # Random UUID for message namespace


class ConversationTable(Base):
    __tablename__ = "conversations"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    messages = relationship(
        "MessageTable", back_populates="conversation", cascade="all, delete-orphan"
    )
    draft_campaigns = relationship(
        "DraftCampaignTable",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )
    campaigns = relationship(
        "CampaignTable",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )


class MessageTable(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key=True, index=True)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    data = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
    conversation = relationship("ConversationTable", back_populates="messages")


class DraftCampaignTable(Base):
    __tablename__ = "draft_campaigns"

    id = Column(String, primary_key=True, index=True)
    type = Column(String, nullable=False)  # 'requirements' or 'copy'
    data = Column(Text, nullable=False)  # JSON data
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    # Relationship with conversation
    conversation = relationship("ConversationTable", back_populates="draft_campaigns")


class CampaignTable(Base):
    __tablename__ = "campaigns"

    id = Column(String, primary_key=True, index=True)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    campaign_name = Column(String, nullable=False)
    product_name = Column(String, nullable=False)
    product_url = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    budget = Column(String, nullable=True)
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=True)
    status = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    
    # API response data
    publisher_id = Column(String, nullable=True)  # ID returned from the ad publisher API
    publisher_data = Column(Text, nullable=True)  # JSON of the full API response
    
    # Relationship with conversation
    conversation = relationship("ConversationTable", back_populates="campaigns")


class SQLAlchemyConversationRepository(ConversationRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: str, title: Optional[str] = None) -> str:
        now = datetime.now(UTC)
        # Use UUID5 - namespace variant with user_id as the name
        conversation_id = str(
            uuid.uuid5(CONVERSATION_NAMESPACE, user_id + str(now.timestamp()))
        )

        if not title:
            title = f"Conversation {now.isoformat()}"
        conversation = ConversationTable(
            id=conversation_id,
            user_id=user_id,
            title=title,
            created_at=now,
            updated_at=now,
        )
        self.session.add(conversation)
        await self.session.commit()
        return conversation_id

    async def get(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        result = await self.session.execute(
            select(ConversationTable).where(ConversationTable.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        if conversation:
            return {
                "id": conversation.id,
                "user_id": conversation.user_id,
                "title": conversation.title,
                "created_at": conversation.created_at.isoformat(),
                "updated_at": conversation.updated_at.isoformat(),
            }
        return None

    async def get_by_user(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get conversations for a user with pagination.

        Args:
            user_id: The user ID to get conversations for
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip (for pagination)

        Returns:
            List of conversations sorted by updated_at in descending order
        """
        result = await self.session.execute(
            select(ConversationTable)
            .where(ConversationTable.user_id == user_id)
            .order_by(ConversationTable.updated_at.desc())
            .offset(offset)
            .limit(limit)
        )
        conversations = result.scalars().all()
        return [
            {
                "id": c.id,
                "user_id": c.user_id,
                "title": c.title,
                "created_at": c.created_at.isoformat(),
                "updated_at": c.updated_at.isoformat(),
            }
            for c in conversations
        ]

    async def delete(self, conversation_id: str) -> bool:
        result = await self.session.execute(
            select(ConversationTable).where(ConversationTable.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        if conversation:
            await self.session.delete(conversation)
            await self.session.commit()
            return True
        return False

    async def update_timestamp(self, conversation_id: str) -> None:
        result = await self.session.execute(
            select(ConversationTable).where(ConversationTable.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        if conversation:
            # Assign the value to the column, not the column itself
            setattr(conversation, "updated_at", datetime.now(UTC))
            await self.session.commit()


class SQLAlchemyMessageRepository(MessageRepository):
    def __init__(
        self, session: AsyncSession, conversation_repo: SQLAlchemyConversationRepository
    ):
        self.session = session
        self.conversation_repo = conversation_repo

    async def get_message_by_id(self, message_id: str) -> Optional[Dict[str, Any]]:
        result = await self.session.execute(
            select(MessageTable).where(MessageTable.id == message_id)
        )
        message = result.scalar_one_or_none()
        if message:
            return {
                "id": message.id,
                "conversation_id": message.conversation_id,
                "created_at": message.created_at.isoformat(),
                "event_data": json.loads(getattr(message, "data")),
            }
        return None

    async def add(
        self,
        conversation_id: str,
        event_data: Dict[str, Any],
        message_id: Optional[str] = None,
    ) -> str:
        now = datetime.now(UTC)
        # Use provided message_id or generate one using UUID5
        if not message_id:
            message_id = str(
                uuid.uuid5(MESSAGE_NAMESPACE, conversation_id + str(now.timestamp()))
            )

        # Check if message with this ID already exists (idempotency check)
        result = await self.session.execute(
            select(MessageTable).where(MessageTable.id == message_id)
        )
        existing_message = result.scalar_one_or_none()

        # If message with this ID already exists, return the existing ID
        if existing_message:
            return message_id

        # Otherwise create a new message
        message = MessageTable(
            id=message_id,
            conversation_id=conversation_id,
            data=json.dumps(event_data),
            created_at=now,
        )
        self.session.add(message)
        await self.session.commit()
        await self.conversation_repo.update_timestamp(conversation_id)
        return message_id

    async def get_by_conversation(
        self, conversation_id: str, limit: int = 20, offset: int = 0
    ) -> List[Dict[str, Any]]:
        result = await self.session.execute(
            select(MessageTable)
            .where(MessageTable.conversation_id == conversation_id)
            .order_by(MessageTable.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        messages = result.scalars().all()
        out = []
        for m in messages:
            msg = {
                "id": m.id,
                "conversation_id": m.conversation_id,
                "created_at": m.created_at.isoformat(),
                "event_data": json.loads(getattr(m, "data")),
            }
            out.append(msg)
        return out

    async def delete_by_conversation(self, conversation_id: str) -> None:
        result = await self.session.execute(
            select(MessageTable).where(MessageTable.conversation_id == conversation_id)
        )
        messages = result.scalars().all()
        for m in messages:
            await self.session.delete(m)
        await self.session.commit()


class SQLAlchemyDraftCampaignRepository(DraftCampaignRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        type: str,
        data: Dict[str, Any],
        conversation_id: str,
    ) -> str:
        now = datetime.now(UTC)
        draft_id = str(uuid.uuid4())

        draft = DraftCampaignTable(
            id=draft_id,
            type=type,
            data=json.dumps(data),
            conversation_id=conversation_id,
            created_at=now,
            updated_at=now,
        )
        self.session.add(draft)
        await self.session.commit()
        return draft_id
        
    async def upsert(
        self,
        type: str,
        data: Dict[str, Any],
        conversation_id: str,
    ) -> Tuple[str, bool]:
        """
        Create or update a draft campaign based on conversation_id and type.
        
        Args:
            type: Type of the draft campaign
            data: Draft campaign data
            conversation_id: ID of the conversation
            
        Returns:
            Tuple of (draft_id, is_new) where is_new is True if a new draft was created
        """
        # Get existing drafts for this conversation with the specified type
        existing_drafts = await self.get_by_conversation(conversation_id, type)
        
        # If there's an existing draft with this type, update it
        if existing_drafts:
            draft_id = existing_drafts[0]["id"]
            await self.update(draft_id, data)
            return draft_id, False
        
        # Otherwise, create a new draft
        draft_id = await self.create(type, data, conversation_id)
        return draft_id, True

    async def get(self, draft_id: str) -> Optional[Dict[str, Any]]:
        result = await self.session.execute(
            select(DraftCampaignTable).where(DraftCampaignTable.id == draft_id)
        )
        draft = result.scalar_one_or_none()
        if draft:
            return {
                "id": draft.id,
                "type": draft.type,
                "data": json.loads(getattr(draft, "data")),
                "conversation_id": draft.conversation_id,
                "created_at": draft.created_at.isoformat(),
                "updated_at": draft.updated_at.isoformat(),
            }
        return None

    async def get_by_conversation(
        self,
        conversation_id: str,
        type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        query = select(DraftCampaignTable).where(
            DraftCampaignTable.conversation_id == conversation_id
        )

        if type:
            query = query.where(DraftCampaignTable.type == type)

        query = query.order_by(DraftCampaignTable.created_at.asc())

        result = await self.session.execute(query)
        drafts = result.scalars().all()

        return [
            {
                "id": d.id,
                "type": d.type,
                "data": json.loads(getattr(d, "data")),
                "conversation_id": d.conversation_id,
                "created_at": d.created_at.isoformat(),
                "updated_at": d.updated_at.isoformat(),
            }
            for d in drafts
        ]

    async def update(
        self,
        draft_id: str,
        data: Dict[str, Any],
    ) -> bool:
        result = await self.session.execute(
            select(DraftCampaignTable).where(DraftCampaignTable.id == draft_id)
        )
        draft = result.scalar_one_or_none()
        if draft:
            setattr(draft, "data", json.dumps(data))
            setattr(draft, "updated_at", datetime.now(UTC))
            await self.session.commit()
            return True
        return False

    async def delete(self, draft_id: str) -> bool:
        result = await self.session.execute(
            select(DraftCampaignTable).where(DraftCampaignTable.id == draft_id)
        )
        draft = result.scalar_one_or_none()
        if draft:
            await self.session.delete(draft)
            await self.session.commit()
            return True
        return False


class SQLAlchemyCampaignRepository(CampaignRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
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
        now = datetime.now(UTC)
        campaign_id = str(uuid.uuid4())

        campaign = CampaignTable(
            id=campaign_id,
            conversation_id=conversation_id,
            campaign_name=campaign_name,
            product_name=product_name,
            product_url=product_url,
            start_date=start_date,
            image_url=image_url,
            description=description,
            budget=budget,
            end_date=end_date,
            status=status if status else "draft",
            publisher_id=publisher_id,
            publisher_data=json.dumps(publisher_data) if publisher_data else None,
            created_at=now,
            updated_at=now,
        )
        self.session.add(campaign)
        await self.session.commit()
        return campaign_id

    async def get(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        result = await self.session.execute(
            select(CampaignTable).where(CampaignTable.id == campaign_id)
        )
        campaign = result.scalar_one_or_none()
        if campaign:
            return self._campaign_to_dict(campaign)
        return None

    async def get_by_conversation(
        self, conversation_id: str
    ) -> List[Dict[str, Any]]:
        result = await self.session.execute(
            select(CampaignTable)
            .where(CampaignTable.conversation_id == conversation_id)
            .order_by(CampaignTable.created_at.desc())
        )
        campaigns = result.scalars().all()
        return [self._campaign_to_dict(c) for c in campaigns]

    async def update(
        self,
        campaign_id: str,
        **kwargs
    ) -> bool:
        result = await self.session.execute(
            select(CampaignTable).where(CampaignTable.id == campaign_id)
        )
        campaign = result.scalar_one_or_none()
        if campaign:
            # Update only provided fields
            for key, value in kwargs.items():
                if hasattr(campaign, key):
                    setattr(campaign, key, value)
            
            # Always update the timestamp
            setattr(campaign, "updated_at", datetime.now(UTC))
            await self.session.commit()
            return True
        return False

    async def delete(self, campaign_id: str) -> bool:
        result = await self.session.execute(
            select(CampaignTable).where(CampaignTable.id == campaign_id)
        )
        campaign = result.scalar_one_or_none()
        if campaign:
            await self.session.delete(campaign)
            await self.session.commit()
            return True
        return False

    async def update_publisher_data(
        self,
        campaign_id: str,
        publisher_id: str,
        publisher_data: Dict[str, Any],
    ) -> bool:
        result = await self.session.execute(
            select(CampaignTable).where(CampaignTable.id == campaign_id)
        )
        campaign = result.scalar_one_or_none()
        if campaign:
            setattr(campaign, "publisher_id", publisher_id)
            setattr(campaign, "publisher_data", json.dumps(publisher_data))
            setattr(campaign, "updated_at", datetime.now(UTC))
            await self.session.commit()
            return True
        return False
        
    def _campaign_to_dict(self, campaign: CampaignTable) -> Dict[str, Any]:
        """Convert a CampaignTable object to a dictionary"""
        result = {
            "id": campaign.id,
            "conversation_id": campaign.conversation_id,
            "campaign_name": campaign.campaign_name,
            "product_name": campaign.product_name,
            "product_url": campaign.product_url,
            "start_date": campaign.start_date,
            "created_at": campaign.created_at.isoformat(),
            "updated_at": campaign.updated_at.isoformat(),
            "status": campaign.status,
        }
        
        # Add optional fields if they exist
        if campaign.image_url is not None:
            result["image_url"] = campaign.image_url
        if campaign.description is not None:
            result["description"] = campaign.description
        if campaign.budget is not None:
            result["budget"] = campaign.budget
        if campaign.end_date is not None:
            result["end_date"] = campaign.end_date
        if campaign.publisher_id is not None:
            result["publisher_id"] = campaign.publisher_id
        if campaign.publisher_data is not None:
            result["publisher_data"] = json.loads(str(campaign.publisher_data))
            
        return result


class SQLAlchemyChatRepository(ChatRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self._conversation_repo = SQLAlchemyConversationRepository(session)
        self._message_repo = SQLAlchemyMessageRepository(
            session, self._conversation_repo
        )
        self._draft_campaign_repo = SQLAlchemyDraftCampaignRepository(session)
        self._campaign_repo = SQLAlchemyCampaignRepository(session)

    @property
    def conversations(self) -> SQLAlchemyConversationRepository:
        return self._conversation_repo

    @property
    def messages(self) -> SQLAlchemyMessageRepository:
        return self._message_repo

    @property
    def draft_campaigns(self) -> SQLAlchemyDraftCampaignRepository:
        return self._draft_campaign_repo
        
    @property
    def campaigns(self) -> SQLAlchemyCampaignRepository:
        return self._campaign_repo
