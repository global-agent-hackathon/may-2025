from typing import List, Optional, Any, Dict, Union, Literal
from pydantic import BaseModel, Field
from constants.enums import ChatRole, ContentType


class ChatMessage(BaseModel):
    role: ChatRole = Field(..., description="Message role")
    content: str = Field(..., description="Message content")

    class Config:
        use_enum_values = True


class ContentBlock(BaseModel):
    type: ContentType = Field(..., description="Content block type")

    class Config:
        use_enum_values = True


class TextContentBlock(ContentBlock):
    type: Literal["text"] = ContentType.TEXT
    text: str = Field(..., description="Text content")


class CSVContentBlock(ContentBlock):
    type: Literal["csv"] = ContentType.CSV
    data: str = Field(..., description="CSV data")
    description: Optional[str] = Field(None, description="Data description")


class ChatRequest(BaseModel):
    threadId: str = Field(..., description="Chat thread identifier")
    formId: Optional[str] = Field(None, description="Form identifier")
    formResponseId: Optional[str] = Field(None, description="Form response identifier")
    message: str = Field(..., description="User message")
    history: List[ChatMessage] = Field(default_factory=list, description="Chat history")
    formConfig: Optional[Any] = Field(None, description="Form configuration")
    formResponse: Optional[Any] = Field(None, description="Form response data")
    userId: Optional[str] = Field(None, description="User identifier for memory integration")


class ChatResponse(BaseModel):
    content_blocks: List[Union[TextContentBlock, CSVContentBlock]] = Field(
        default_factory=list, 
        description="Response content blocks"
    )
    sourceQuery: Optional[str] = Field(None, description="Source SQL query")
    timestamp: Optional[str] = Field(None, description="Response timestamp") 