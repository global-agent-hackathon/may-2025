# Database
In this document, I will discuss about the setup of the database in the `Supabase` and creating the schema for `SQLModel`. The database is used to store and retireve the mails securely.
## Setup
### Supabase
* Visit the Supabase platform
* Create a new project
* In top panel of the project there will be `connect` button and in that we can get the environment variable values like `DATABASE_URL` and store it in `.env` file
### Cryptography
To encrypt the content of the mails in the database, we use `Fernet` key from the `cryptography` python package.
* Run the below script to generate the one time key for the encryption and decryption and save the key in the `.env` file
```py
from cryptography.fernet import Fernet

key = Fernet.generate_key()
with open(".env", "a") as env_file:
    env_file.write(f"\nENCRYPTION_KEY={key.decode()}\n")
```
* To encrypt and decrypt the content, the logic is implemented in the `backend/core/utils.py` file, in which we have two functions namely `encrypt_value` and `decrypt_value`
### Initialization
* Initialize the database session
```py
from sqlmodel import create_engine, SQLModel, Session
from core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)
```
## Schema
This app needs two models `Users` and `Mail` models. The below code is for the `SQLModels`
```py
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
```