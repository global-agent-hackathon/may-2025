import uuid
from typing import AsyncGenerator, Optional

from sqlalchemy import Boolean, Column, String
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select

from utils.config import config

from .models import User, UserCreate

# Set up the database
Base = declarative_base()


# SQLAlchemy ORM model for User
class UserTable(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    picture = Column(String, nullable=True)
    google_id = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)


# Create async engine and session
engine = create_async_engine(config.database_url, echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


# Initialize database
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Session dependency
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


# User database operations
async def get_user_by_google_id(
    session: AsyncSession, google_id: str
) -> Optional[User]:
    """Get a user by Google ID"""
    result = await session.execute(
        select(UserTable).filter(UserTable.google_id == google_id)
    )
    user_db = result.scalars().first()
    if not user_db:
        return None
    return User(
        id=str(user_db.id),
        email=str(user_db.email),
        name=str(user_db.name),
        picture=str(user_db.picture),
        google_id=str(user_db.google_id),
        is_active=bool(user_db.is_active),
    )


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    """Get a user by email using async SQLAlchemy."""
    try:
        result = await session.execute(
            select(UserTable).where(UserTable.email == email)
        )
        user_db = result.scalar_one_or_none()
        if not user_db:
            return None
        return User(
            id=str(user_db.id),
            email=str(user_db.email),
            name=str(user_db.name),
            picture=str(user_db.picture),
            google_id=str(user_db.google_id),
            is_active=bool(user_db.is_active),
        )
    except Exception:
        return None


async def create_user(session: AsyncSession, user_create: UserCreate) -> User:
    """Create a new user"""
    user_id = str(uuid.uuid4())
    user_db = UserTable(
        id=user_id,
        email=user_create.email,
        name=user_create.name,
        picture=user_create.picture,
        google_id=user_create.google_id,
        is_active=True,
    )
    session.add(user_db)
    await session.commit()
    await session.refresh(user_db)

    return User(
        id=str(user_db.id),
        email=str(user_db.email),
        name=str(user_db.name),
        picture=str(user_db.picture),
        google_id=str(user_db.google_id),
        is_active=bool(user_db.is_active),
    )


async def get_or_create_user(session: AsyncSession, user_create: UserCreate) -> User:
    """Get existing user or create a new one"""
    existing_user = await get_user_by_google_id(session, user_create.google_id)
    if existing_user:
        return existing_user
    return await create_user(session, user_create)
