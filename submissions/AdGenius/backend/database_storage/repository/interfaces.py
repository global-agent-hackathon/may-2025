"""
Repository interfaces for database storage

This module defines the abstract interfaces for the database storage repositories.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple


class ConversationRepository(ABC):
    """Interface for conversation storage operations"""

    @abstractmethod
    async def create(self, user_id: str, title: Optional[str] = None) -> str:
        """Create a new conversation and return its ID"""
        pass

    @abstractmethod
    async def get(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get a conversation by ID"""
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def delete(self, conversation_id: str) -> bool:
        """Delete a conversation"""
        pass

    @abstractmethod
    async def update_timestamp(self, conversation_id: str) -> None:
        """Update the conversation's timestamp"""
        pass


class MessageRepository(ABC):
    """Interface for message storage operations"""

    @abstractmethod
    async def add(
        self,
        conversation_id: str,
        event_data: Dict[str, Any],
        message_id: Optional[str] = None,
    ) -> str:
        """Add a message to a conversation and return its ID

        Args:
            conversation_id: The conversation ID to add the message to
            event_data: The message data
            message_id: Optional custom message ID for idempotency

        Returns:
            The ID of the added message
        """
        pass

    @abstractmethod
    async def get_by_conversation(
        self, conversation_id: str, limit: int = 20, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get messages for a conversation with pagination"""
        pass

    @abstractmethod
    async def get_message_by_id(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get a message by its unique message_id"""
        pass

    @abstractmethod
    async def delete_by_conversation(self, conversation_id: str) -> None:
        """Delete all messages for a conversation"""
        pass


class CampaignRepository(ABC):
    """Interface for campaign storage operations"""

    @abstractmethod
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
        """Create a new campaign and return its ID"""
        pass

    @abstractmethod
    async def get(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get a campaign by ID"""
        pass

    @abstractmethod
    async def get_by_conversation(
        self, conversation_id: str
    ) -> List[Dict[str, Any]]:
        """Get campaigns for a conversation"""
        pass

    @abstractmethod
    async def update(
        self,
        campaign_id: str,
        **kwargs
    ) -> bool:
        """Update a campaign with new values"""
        pass

    @abstractmethod
    async def delete(self, campaign_id: str) -> bool:
        """Delete a campaign"""
        pass

    @abstractmethod
    async def update_publisher_data(
        self,
        campaign_id: str,
        publisher_id: str,
        publisher_data: Dict[str, Any],
    ) -> bool:
        """Update a campaign with data from the ad publisher API"""
        pass


class ChatRepository(ABC):
    """Interface for combined chat storage operations"""

    @property
    @abstractmethod
    def conversations(self) -> ConversationRepository:
        """Get the conversation repository"""
        pass

    @property
    @abstractmethod
    def messages(self) -> MessageRepository:
        """Get the message repository"""
        pass

    @property
    @abstractmethod
    def draft_campaigns(self) -> "DraftCampaignRepository":
        """Get the draft campaign repository"""
        pass

    @property
    @abstractmethod
    def campaigns(self) -> CampaignRepository:
        """Get the campaign repository"""
        pass


class DraftCampaignRepository(ABC):
    """Interface for draft campaign storage operations"""

    @abstractmethod
    async def create(
        self,
        type: str,
        data: Dict[str, Any],
        conversation_id: str,
    ) -> str:
        """Create a new draft campaign and return its ID"""
        pass

    @abstractmethod
    async def get(self, draft_id: str) -> Optional[Dict[str, Any]]:
        """Get a draft campaign by ID"""
        pass

    @abstractmethod
    async def get_by_conversation(
        self,
        conversation_id: str,
        type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get draft campaigns for a conversation with optional type filter"""
        pass

    @abstractmethod
    async def update(
        self,
        draft_id: str,
        data: Dict[str, Any],
    ) -> bool:
        """Update a draft campaign's data"""
        pass

    @abstractmethod
    async def delete(self, draft_id: str) -> bool:
        """Delete a draft campaign"""
        pass
        
    @abstractmethod
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
        pass
