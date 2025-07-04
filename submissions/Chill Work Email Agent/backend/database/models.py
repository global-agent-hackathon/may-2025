from typing import Optional, List
from sqlmodel import Field, Relationship, SQLModel, Column, String
from sqlalchemy.dialects.postgresql import TEXT,TIMESTAMP,ARRAY
from sqlalchemy import UniqueConstraint
from enum import Enum
from datetime import datetime, timezone

class ProviderType(str, Enum):
    GOOGLE = "google"
    EMAIL_PASSWORD = "email_password"

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True, max_length=255)
    provider_type: ProviderType = Field(default=ProviderType.GOOGLE, index=True)
    provider_id: Optional[str] = Field(default=None, index=True, max_length=255)
    name: Optional[str] = Field(default=None, max_length=255)
    picture: Optional[str] = Field(default=None)
    access_token: Optional[str] = Field(default=None, sa_column=Column(TEXT))
    refresh_token: Optional[str] = Field(default=None, sa_column=Column(TEXT))
    category_instruction: Optional[str] = Field(
        default=None,
        sa_column=Column(TEXT),
        description="User's instruction for AI to label emails."
    )
    is_active: bool = Field(default=True)

class User(UserBase, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    hashed_password: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
        nullable=False
    )
    mails: List["Mail"] = Relationship(back_populates="user")

class UserCreate(UserBase):
    password: Optional[str] = None

class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

class UserUpdate(SQLModel):
    email: Optional[str] = None
    name: Optional[str] = None
    picture: Optional[str] = None
    category_instruction: Optional[str] = None
    is_active: Optional[bool] = None

class MailTagValue(str, Enum):
    INBOX = "Inbox"
    IMPORTANT = "Important"
    ARCHIVE = "Archive"
    SENT = "Sent"

class MailBase(SQLModel):
    gmail_message_id: str = Field(index=True, description="Gmail's unique ID for the message")
    from_address: str = Field(max_length=255)
    from_name: Optional[str] = Field(default=None, max_length=255)
    to_address: Optional[str] = Field(max_length=255)
    to_name: Optional[str] = Field(default=None, max_length=255)
    message_timestamp: datetime = Field(
        sa_column=Column(TIMESTAMP(timezone=True),index=True),
        description="Timestamp when the message was received or sent (UTC recommended)"
    )
    subject: Optional[str] = Field(default=None, sa_column=Column(TEXT))
    snippet: Optional[str] = Field(default=None, sa_column=Column(TEXT))
    content_html: Optional[str] = Field(default=None, sa_column=Column(TEXT), description="HTML content of the mail")
    content_plain: Optional[str] = Field(default=None, sa_column=Column(TEXT), description="Plain text content of the mail")
    tags: List[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))


class Mail(MailBase, table=True):
    __tablename__ = "mails"
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    user: Optional[User] = Relationship(back_populates="mails")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
        nullable=False
    )
    __table_args__ = (
        UniqueConstraint('user_id', 'gmail_message_id', name='_user_gmail_message_uc'),
    )

class MailCreate(MailBase):
    pass

class MailRead(MailBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

class MailUpdate(SQLModel):
    tags: Optional[List[str]] = None