from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class MemorySearchRequest(BaseModel):
    """Request model for searching memories."""
    user_id: str = Field(..., description="Unique identifier for the user")
    query: str = Field(..., description="Search query")
    limit: int = Field(default=10, description="Maximum number of results")
    memory_type: Optional[str] = Field(default=None, description="Filter by memory type")


class MemorySearchResponse(BaseModel):
    """Response model for memory search."""
    memories: List[Dict[str, Any]] = Field(..., description="List of relevant memories")
    total_count: int = Field(..., description="Total number of memories found")


class AddConversationMemoryRequest(BaseModel):
    """Request model for adding conversation memory."""
    user_id: str = Field(..., description="Unique identifier for the user")
    user_message: str = Field(..., description="The user's message")
    assistant_response: str = Field(..., description="The assistant's response")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")


class AddFormInteractionMemoryRequest(BaseModel):
    """Request model for adding form interaction memory."""
    user_id: str = Field(..., description="Unique identifier for the user")
    form_id: str = Field(..., description="Form identifier")
    form_title: str = Field(..., description="Form title")
    interaction_type: str = Field(..., description="Type of interaction")
    details: Dict[str, Any] = Field(..., description="Additional details")


class AddUserPreferenceMemoryRequest(BaseModel):
    """Request model for adding user preference memory."""
    user_id: str = Field(..., description="Unique identifier for the user")
    preference_type: str = Field(..., description="Type of preference")
    preference_value: Any = Field(..., description="The preference value")
    context: Optional[str] = Field(default=None, description="Additional context")


class MemoryOperationResponse(BaseModel):
    """Response model for memory operations."""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Status message")


class UserContextRequest(BaseModel):
    """Request model for getting user context."""
    user_id: str = Field(..., description="Unique identifier for the user")
    query: str = Field(..., description="Current user query")


class UserContextResponse(BaseModel):
    """Response model for user context."""
    context: str = Field(..., description="Formatted context string")
    memories_count: int = Field(..., description="Number of memories used for context")


class FormHistoryRequest(BaseModel):
    """Request model for getting form history."""
    user_id: str = Field(..., description="Unique identifier for the user")
    form_id: Optional[str] = Field(default=None, description="Specific form ID to filter by")


class FormHistoryResponse(BaseModel):
    """Response model for form history."""
    interactions: List[Dict[str, Any]] = Field(..., description="List of form interactions")
    total_count: int = Field(..., description="Total number of interactions")


class UserPreferencesResponse(BaseModel):
    """Response model for user preferences."""
    preferences: Dict[str, Any] = Field(..., description="Dictionary of user preferences")
    total_count: int = Field(..., description="Total number of preferences") 