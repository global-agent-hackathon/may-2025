from typing import Optional
from pydantic import Field
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(
    __file__
).parent.parent.parent  # str(Path(__file__).parent.parent.parent)

ENV_FILE = ROOT_DIR / ".env"  # dynamically choose the file


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8")
    """Central configuration settings for the application."""
    # --- Core Application Settings ---
    APP_NAME: str = "Slack Meeting Summarizer"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    # --- AI/ML Services ---
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS: int = Field(1536, env="EMBEDDING_DIMENSIONS")
    EMBEDDING_PROVIDER: str = "openai"
    LLM_MODEL_NAME: str = "gpt-4o"
    OPENAI_API_KEY: str = Field(None, env="OPENAI_API_KEY")

    # --- Data Storage ---
    BUCKET_NAME: str = Field("team-meeting-hackathon", env="BUCKET_NAME")

    # --- Qdrant Vector Database ---
    QDRANT_URL: str = Field("http://localhost:6333", env="QDRANT_URL")
    QDRANT_API_KEY: Optional[str] = Field(None, env="QDRANT_API_KEY")
    QDRANT_COLLECTION_NAME: str = Field(
        "meetings-hackathon", env="QDRANT_COLLECTION_NAME"
    )

    # --- Slack configuration ---
    SLACK_TOKEN: str = Field(None, env="SLACK_TOKEN")
    SLACK_SIGNING_SECRET: str = Field(None, env="SLACK_SIGNING_SECRET")
    SLACK_BOT_USER_ID: str = Field(None, env="SLACK_BOT_USER_ID")

    # --- Trello configuration ---
    TRELLO_API_KEY: str = Field(None, env="TRELLO_API_KEY")
    TRELLO_API_SECRET: str = Field(None, env="TRELLO_API_SECRET")
    TRELLO_TOKEN: str = Field(None, env="TRELLO_TOKEN")

    # --- Google configuration ---
    # GOOGLE_PROJECT_ID: str = Field(None, env="GOOGLE_PROJECT_ID")
    # GOOGLE_CLIENT_ID: str = Field(None, env="GOOGLE_CLIENT_ID")
    # GOOGLE_CLIENT_SECRET: str = Field(None, env="GOOGLE_CLIENT_SECRET")


# Instantiate settings
settings = Settings()
