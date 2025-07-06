import logging
import uvicorn
import asyncio
import threading

from app import app
from cron import update_cache
from src.utils.cache import RedisCache
from config import LOG_LEVEL, CRON_INTERVAL, REDIS_HOST, REDIS_PORT, REDIS_PASSWORD

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def check_and_update_cache():
    """Check if cache is stale and update if needed"""
    logger.info("Checking cache freshness")
    cache = RedisCache(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
    
    if cache.is_cache_stale(CRON_INTERVAL):
        logger.info("Cache is stale or empty, running initial update")
        await update_cache()
    else:
        logger.info("Cache is fresh, skipping initial update")

def start_scheduler():
    """Start the background scheduler for cache updates"""
    logger.info("Starting background cache update scheduler")
    from apscheduler.schedulers.background import BackgroundScheduler
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: asyncio.run(update_cache()), 'interval', minutes=CRON_INTERVAL)
    scheduler.start()
    
    asyncio.run(check_and_update_cache())
    
    logger.info(f"Scheduler started, will update cache every {CRON_INTERVAL} minutes")
    return scheduler

if __name__ == "__main__":
    scheduler_thread = threading.Thread(target=start_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    logger.info("Starting FastAPI application")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)