import os
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings for Superwizard Server"""
    
    # Application Configuration
    app_name: str = "Superwizard Server"
    version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Server Configuration
    server_port: int = int(os.getenv("SERVER_PORT", "7777"))
    
    # OpenRouter Configuration
    openrouter_api_key: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    
    # Database Configuration
    db_user: str = os.getenv("DB_USER", "superwizard")
    db_password: str = os.getenv("DB_PASSWORD", "superwizard123")
    db_name: str = os.getenv("DB_NAME", "superwizard_db")
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "5433"))
    
    # Telemetry Configuration
    telemetry_enabled: bool = os.getenv("TELEMETRY_ENABLED", "false").lower() == "true"
    
    class Config:
        env_file = ".env"

settings = Settings() 