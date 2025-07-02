from pydantic import BaseModel, model_validator
from typing import List, Optional, Dict, Any, Literal, Union
from datetime import datetime
from backend.models.base.chat import ChatThreadBase, ChatMessageBase, MessageMetadata
from backend.models.response.finance import (
    RevenueAnalysisResponse,
    ExpenseAnalysisResponse,
    ProfitMarginsResponse,
)
import json


class LastMessage(BaseModel):
    content: str
    sender: Literal["user", "assistant"]
    timestamp: datetime
    user_id: Optional[str] = None
    user_name: Optional[str] = None


class ChatThread(ChatThreadBase):
    message_count: int
    last_message: Optional[LastMessage] = None


class ChatThreadList(BaseModel):
    threads: List[ChatThread]
    total: int


class ChatThreadWithoutMessages(ChatThreadBase):
    pass


class ThreadSummary(ChatThreadBase):
    last_message: Optional[LastMessage] = None
    message_count: Optional[int] = 0


class ChatMessage(ChatMessageBase):
    metadata: Optional[MessageMetadata] = None


class MessageResponse(ChatMessageBase):
    metadata: Optional[MessageMetadata] = None
    iframe_url: Optional[list[str]] = None  # Explicitly declare

    @model_validator(mode="after")
    def set_iframe_url(self):
        """Extracts iframe URLs from tool metadata and attaches them to the message."""
        result_iframe = []
        if self.metadata and getattr(self.metadata, "tools", None):
            for tool in self.metadata.tools:
                content = tool.get("result")
                if content and isinstance(content, str):
                    try:
                        content = json.loads(content)
                    except Exception:
                        continue
                if isinstance(content, dict) and content.get("iframe_url"):
                    result_iframe.append(content["iframe_url"])
        self.iframe_url = result_iframe or None
        return self


class ChatThreadWithMessages(ChatThreadBase):
    messages: Optional[list[MessageResponse]] = None

    @model_validator(mode="after")
    def set_iframe_url(self):
        """
        - Collects iframe URLs from tool messages and attaches them to the next assistant message.
        - Removes tool messages from the message list.
        """
        result_iframe = []
        filtered_messages = []
        for message in self.messages:
            if getattr(message, "sender", None) == "tool":
                content = getattr(message, "content", None)
                if content and isinstance(content, str):
                    try:
                        content = json.loads(content)
                    except Exception:
                        continue
                if isinstance(content, dict) and content.get("iframe_url"):
                    result_iframe.append(content["iframe_url"])
                continue  # Always skip tool messages
            if result_iframe and getattr(message, "sender", None) == "assistant":
                message.iframe_url = result_iframe.copy()
                result_iframe = []
            filtered_messages.append(message)
        self.messages = filtered_messages
        return self


AgentResponse = Union[
    RevenueAnalysisResponse, ExpenseAnalysisResponse, ProfitMarginsResponse
]


class AnalysisResponse(BaseModel):
    summary: str
    data: dict
    sources: List[str]


class AssistantMessageResponse(ChatMessageBase):
    metadata: MessageMetadata = MessageMetadata(references=[], analysis={})


class FileUploadInitiateResponse(BaseModel):
    file_id: str
    upload_url: str
    expires: datetime


class FileUploadCompleteResponse(BaseModel):
    id: str
    name: str
    type: str
    size: int
    status: Literal["processing", "ready", "error"]
    url: str
    created_at: datetime
    thread_id: Optional[str] = None
    processing_details: Dict[str, Any]
