"""
Database storage package for Ad Genius

This package provides database storage functionality for the application.
"""

from database_storage.database import (
    get_session,
    get_repository,
    init_chat_db,
    create_conversation,
    get_conversation,
    get_user_conversations,
    delete_conversation,
    add_message,
    get_message_by_id,
    get_conversation_messages,
    create_draft_campaign,
    upsert_draft_campaign,
    get_draft_campaign,
    get_conversation_draft_campaigns,
    update_draft_campaign,
    delete_draft_campaign,
    create_campaign,
    get_campaign,
    get_conversation_campaigns,
    update_campaign,
    delete_campaign,
    update_campaign_publisher_data,
)

__all__ = [
    "get_session",
    "get_repository",
    "init_chat_db",
    "create_conversation",
    "get_conversation",
    "get_user_conversations",
    "delete_conversation",
    "add_message",
    "get_message_by_id",
    "get_conversation_messages",
    "create_draft_campaign",
    "upsert_draft_campaign",
    "get_draft_campaign",
    "get_conversation_draft_campaigns",
    "update_draft_campaign",
    "delete_draft_campaign",
    "create_campaign",
    "get_campaign",
    "get_conversation_campaigns",
    "update_campaign",
    "delete_campaign",
    "update_campaign_publisher_data",
]