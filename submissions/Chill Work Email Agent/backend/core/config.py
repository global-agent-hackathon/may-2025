import os
import secrets
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class Settings(BaseSettings):
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    REDIRECT_URI: str = os.getenv("REDIRECT_URI", "")
    FRONTEND_DASHBOARD_URL: str = os.getenv("FRONTEND_DASHBOARD_URL", "")
    SESSION_SECRET_KEY: str = os.getenv("SESSION_SECRET_KEY", secrets.token_urlsafe(32)) 
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY","")
    
    SCOPES: list[str] = [
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/gmail.readonly",
        "openid"
    ]

    AUTHORIZATION_URL: str = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL: str = "https://oauth2.googleapis.com/token"
    USERINFO_URL: str = "https://www.googleapis.com/oauth2/v3/userinfo"
    
    MAX_GMAIL_RESULTS_PER_QUERY: int = 5
    MAX_MESSAGES_TO_PROCESS_FULL: int = 5
    
    CORS_ALLOW_ORIGINS: list[str] = [os.getenv("CORS_ALLOWED_ORIGIN", "http://localhost:3000")]
    
    MAILTRAP_SMTP_HOST: str
    MAILTRAP_SMTP_PORT: int
    MAILTRAP_SMTP_USERNAME: str
    MAILTRAP_SMTP_PASSWORD: str
    MAIL_FROM_ADDRESS: str
    
    ENCRYPTION_KEY: str
    
    WEAVIATE_URL: str
    WEAVIATE_API_KEY: str
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

if not all([
    settings.GOOGLE_CLIENT_ID, 
    settings.GOOGLE_CLIENT_SECRET, 
    settings.REDIRECT_URI, 
    settings.FRONTEND_DASHBOARD_URL
]):
    raise ValueError("Environment variable related to Google OAuth2 is missing. Check your .env file and core/config.py.")

if not all([
    settings.DATABASE_URL,
    settings.CORS_ALLOW_ORIGINS,
    settings.GROQ_API_KEY,
    settings.ENCRYPTION_KEY
]):
    raise ValueError("Environmnet variable related to database or Groq is missing. Check you r.env file and core/config.py")

if not all([
   settings.MAILTRAP_SMTP_HOST,
    settings.MAILTRAP_SMTP_PORT,
    settings.MAILTRAP_SMTP_USERNAME,
    settings.MAILTRAP_SMTP_PASSWORD,
    settings.MAIL_FROM_ADDRESS 
]):
    raise ValueError("Environment variable related to Mailtrap SMTP is missing. Check your .env file and core/config.py")

if not all([
    settings.WEAVIATE_URL,
    settings.WEAVIATE_API_KEY
]):
    raise ValueError("Environment variable related to Weaviate is missing. Check your .env file and core/config.py")