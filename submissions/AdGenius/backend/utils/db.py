"""
Database utilities

This module now delegates to the chat_assistant.database module to avoid code duplication.
It is maintained for backward compatibility.
"""

import logging
import os

from database_storage.database import (
    add_message,
    create_conversation,
    delete_conversation,
    get_conversation,
    get_conversation_messages,
    get_repository,
    get_user_conversations,
    init_chat_db,
)

# Configure logging
logger = logging.getLogger(__name__)

# Export all the delegated functions to maintain backward compatibility
__all__ = [
    "init_chat_db",
    "create_conversation",
    "add_message",
    "get_conversation",
    "get_conversation_messages",
    "get_user_conversations",
    "delete_conversation",
    "get_repository",
]


def ensure_sqlite_dir_exists(database_url: str):
    """
    If the database_url is for SQLite, ensure the parent directory exists.
    Handles both relative and absolute paths.
    """
    if database_url.startswith("sqlite:///"):
        path = database_url.replace("sqlite:///", "", 1)
        # For absolute paths, path may start with /
        if path.startswith("/"):
            db_path = path
        else:
            db_path = os.path.abspath(path)
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
