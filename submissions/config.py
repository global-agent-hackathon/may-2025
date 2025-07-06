import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "crypto-news51.p.rapidapi.com")
RAPID_API_URL = f"https://{RAPIDAPI_HOST}/api/v1/crypto/articles"

TWEETSCOUT_API_KEY = os.getenv("TWEETSCOUT_API_KEY", "")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "123")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
CACHE_TTL = int(os.getenv("CACHE_TTL", str(60 * 60 * 24)))
CRON_INTERVAL = int(os.getenv("CRON_INTERVAL", "60"))

API_RATE_LIMIT = int(os.getenv("API_RATE_LIMIT", "100"))