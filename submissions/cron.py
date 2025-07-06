import logging
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.agent import CryptoAgent
from src.tools import CryptoNewsTool
from src.utils.cache import RedisCache
from config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, CRON_INTERVAL, LOG_LEVEL

logger = logging.getLogger(__name__)

async def update_cache():
    """Update Redis cache with fresh articles"""
    try:
        logger.info("Starting scheduled cache update")
        start_time = datetime.now()
        
        cache = RedisCache(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
        news_tool = CryptoNewsTool(cache)
        
        success = await news_tool.update_cache()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        if success:
            logger.info(f"Cache update completed successfully in {duration:.2f} seconds")
        else:
            logger.warning(f"Cache update completed with issues in {duration:.2f} seconds")
            
    except Exception as e:
        logger.error(f"Error during scheduled cache update: {str(e)}", exc_info=True)

async def main():
    """Start the scheduler"""
    logger.info("Initializing crypto news cache scheduler")
    
    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_cache, 'interval', minutes=CRON_INTERVAL, id='update_cache')
    scheduler.start()
    
    logger.info(f"Scheduler started, will update cache every {CRON_INTERVAL} minutes")
    
    cache = RedisCache(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
    if cache.is_cache_stale(CRON_INTERVAL):
        logger.info("Cache is stale or empty, running initial update")
        await update_cache()
    else:
        logger.info("Cache is fresh, skipping initial update")
    
    try:
        while True:
            await asyncio.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler shutdown requested")
        scheduler.shutdown()
        logger.info("Scheduler shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())