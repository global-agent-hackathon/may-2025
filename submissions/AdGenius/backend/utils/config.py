import os
from functools import lru_cache
from typing import Any, Dict, Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Define environment types
class Environment:
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


# Environment setting
ENV = os.getenv("ENV", "development")


@lru_cache()
def get_environment() -> str:
    """Get the current environment."""
    return ENV.lower()


@lru_cache()
def is_production() -> bool:
    """Check if the application is running in production."""
    return get_environment() == Environment.PRODUCTION


@lru_cache()
def is_testing() -> bool:
    """Check if the application is running in testing mode."""
    return get_environment() == Environment.TESTING


@lru_cache()
def is_development() -> bool:
    """Check if the application is running in development mode."""
    return get_environment() == Environment.DEVELOPMENT


class AppConfig:
    """Application configuration class."""

    def __init__(self):
        # Server settings
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", 8000))
        self.debug = self._parse_bool(os.getenv("DEBUG", "false"))
        self.environment = get_environment()

        # Security settings
        self.secret_key = os.getenv("SECRET_KEY", "")
        self.algorithm = os.getenv("ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24)
        )  # 1 day

        # Database settings
        self.database_url = os.getenv(
            "DATABASE_URL", "sqlite+aiosqlite:///./tmp/adgenius.db"
        )

        # Google OAuth settings
        self.google_client_id = os.getenv("GOOGLE_CLIENT_ID", "")
        self.google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
        self.google_redirect_uri = os.getenv(
            "GOOGLE_REDIRECT_URI", "http://localhost:8000/api/v1/auth/callback"
        )

        # CORS settings
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")

        # Logging settings
        self.log_level = os.getenv("LOG_LEVEL", "info" if is_production() else "debug")
        self.log_format = os.getenv(
            "LOG_FORMAT", None
        )  # Use default from logger.py if not specified
        self.log_to_file = self._parse_bool(os.getenv("LOG_TO_FILE", "false"))
        self.log_dir = os.getenv("LOG_DIR", "./logs")

        # AWS Bedrock Configuration
        self.aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_region = os.getenv("AWS_REGION", "us-east-1")

    def _parse_bool(self, value: Optional[str]) -> bool:
        """Parse string to boolean."""
        if not value:
            return False
        return value.lower() in ("yes", "true", "t", "1", "on")

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            key: value
            for key, value in self.__dict__.items()
            # Filter out private attributes
            if not key.startswith("_")
        }


@lru_cache()
def get_config() -> AppConfig:
    """Get application configuration singleton."""
    return AppConfig()


# Export config as a convenient singleton
config = get_config()


def get_aws_credentials() -> Dict[str, str]:
    """Get AWS credentials for Bedrock"""
    return {
        "access_key": config.aws_access_key or "",
        "secret_key": config.aws_secret_key or "",
        "region": config.aws_region or "",
    }
