"""
Chat Assistant API endpoints package

This package contains modules for the various endpoint domains of the Chat Assistant API:
- conversations: Conversation management (create, list, get, delete)
- messages: Message operations (add, list)
- streaming: Streaming chat functionality
"""

from fastapi import APIRouter

# Import all endpoint modules
from . import conversations, draft_campaigns, messages, streaming

# Create a unified router that includes all endpoint routers
chat_router = APIRouter(prefix="/chat", tags=["chat"])
chat_router.include_router(conversations.router)
chat_router.include_router(messages.router)
chat_router.include_router(streaming.router)
chat_router.include_router(draft_campaigns.router)
