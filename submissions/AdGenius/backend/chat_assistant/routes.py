"""
Chat Routes for the AdGenius API

This module is a compatibility layer that re-exports the chat endpoints
from the endpoints package. New code should import directly from that package.
"""

import logging

# Import the chat router and setup function from the endpoints package
from chat_assistant.endpoints import chat_router

# Configure logging
logger = logging.getLogger(__name__)

# Export the router and setup function for backwards compatibility
router = chat_router
# Keep the reference to setup_chat_db so it's exported as-is
