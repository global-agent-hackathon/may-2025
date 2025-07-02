from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from agno.models.message import Citations
from pydantic import Field


class ChatThreadBase(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None  # User ID or name of thread creator


class ChatMessageBase(BaseModel):
    id: Optional[str] = None
    content: Optional[str] = None
    sender: Literal["user", "assistant", "tool"]
    iframe_url: Optional[list[str]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    user_id: Optional[str] = None  # User ID associated with the message
    user_name: Optional[str] = None  # User name/display name


class Attachment(BaseModel):
    id: str
    name: Optional[str] = None
    type: Optional[str] = None
    size: Optional[int] = None
    url: Optional[str] = None


class Reference(BaseModel):
    title: str
    url: str


class AssociatedDocument(BaseModel):
    id: str
    name: str
    insights: List[str]
    confidence: float
    extracted_data: Dict[str, Any]


class AgnoMessage(BaseModel):
    role: Optional[str] = None
    content: Optional[str] = None


class MessageMetadata(BaseModel):
    tools: Optional[List[Dict[str, Any]]] = None
    formatted_tool_calls: Optional[List[str]] = None
    citations: Optional[Citations] = None
    messages: Optional[List[AgnoMessage]] = None
    model: Optional[str] = None
