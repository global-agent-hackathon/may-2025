import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    # Otras configuraciones pueden ir aquí
    FIRECRAWL_API_KEY = os.environ.get('FIRECRAWL_API_KEY')
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

class TestConfig(Config):
    TESTING = True
    DEBUG = True
    # Use a separate database for testing if necessary
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///../data/test_agent_sessions.db'
    WTF_CSRF_ENABLED = False # Disable CSRF for testing forms if you have them
    DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data') # Path to data dir from config.py location
    # Ensure dummy API keys are set if not in .env for testing agent initialization
    # These can be overridden by actual .env values if present, or by specific test mocks
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', 'dummy_google_key_for_testing')
    FIRECRAWL_API_KEY = os.environ.get('FIRECRAWL_API_KEY', 'dummy_firecrawl_key_for_testing') 