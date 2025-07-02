from pydantic import BaseModel
from typing import List, Optional


class CreateThreadRequest(BaseModel):
    title: Optional[str] = None
    created_by: Optional[str] = None  # User ID or name of the thread creator


class UpdateThreadRequest(BaseModel):
    title: str


class AttachmentRequest(BaseModel):
    id: str


class MessageContext(BaseModel):
    company_id: Optional[str] = None


class SendMessageRequest(BaseModel):
    content: str
    attachments: Optional[List[AttachmentRequest]] = None
    user_id: Optional[str] = None  # User ID associated with the message
    user_name: Optional[str] = None  # User name/display name
