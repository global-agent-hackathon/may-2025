#!/usr/bin/env python3
"""
Script to drop chat-related tables.
This will completely reset the chat data structure.
"""
import os
import psycopg
import logging
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Tables to drop (update this list if you have different table names)
CHAT_TABLES = [
    "ChatMessage",
    "ChatThread"
]

def sanitize_db_url(url):
    """Sanitize database URL for psycopg."""
    parsed = urlparse(url.strip().strip('"'))
    # Keep only essential parts + sslmode=require
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?sslmode=require"

def main():
    # Get database URL from environment
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        logger.error("DATABASE_URL environment variable is not set")
        return False

    # Sanitize the URL for database connection
    sanitized_url = sanitize_db_url(db_url)
    parsed = urlparse(sanitized_url)
    logger.info(f"Connecting to database: {sanitized_url.replace(parsed.netloc, '[REDACTED]')}")

    # Drop tables
    try:
        with psycopg.connect(sanitized_url) as conn:
            with conn.cursor() as cur:
                for table in CHAT_TABLES:
                    logger.info(f"Dropping table: {table}")
                    cur.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')
                conn.commit()
        logger.info("All chat tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping tables: {e}")
        return False
        
    logger.info("=" * 80)
    logger.info("Chat tables have been successfully dropped.")
    logger.info("")
    logger.info("NEXT STEPS:")
    logger.info("1. Start your application to trigger automatic table creation")
    logger.info("   or run your migration tool manually.")
    logger.info("")
    logger.info("   For example, if using Prisma:")
    logger.info("   cd ../flux-main && npx prisma db push")
    logger.info("=" * 80)
    
    return True

if __name__ == "__main__":
    main() 