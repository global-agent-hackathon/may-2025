import logging
import os
import httpx
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from ..utils.cache import RedisCache
from ..models import CryptoNewsResponse
from ..utils.time_utils import extract_time_period
from .base_tool import BaseTool
from config import CRON_INTERVAL

logger = logging.getLogger(__name__)

class CryptoNewsTool(BaseTool):
    name = "crypto_news"
    description = "Get the latest cryptocurrency news articles. Use this for general market updates and trends."
    
    def __init__(self, redis_cache: RedisCache):
        super().__init__()
        self.cache = redis_cache
        self.api_key = os.getenv("RAPIDAPI_KEY", "")
        self.api_host = os.getenv("RAPIDAPI_HOST", "crypto-news51.p.rapidapi.com")
        self.api_url = "https://crypto-news51.p.rapidapi.com/api/v1/crypto/articles"
    
    async def fetch_articles(self, page: int = 1, limit: int = 100, time_frame: str = "24h") -> List[Dict[str, Any]]:
        logger.info(f"Fetching crypto news articles from API: page={page}, limit={limit}, time_frame={time_frame}")
        
        try:
            if not self.api_key:
                logger.error("RAPIDAPI_KEY is not set")
                return []
            
            headers = {
                "x-rapidapi-host": self.api_host,
                "x-rapidapi-key": self.api_key
            }
            
            params = {
                "page": str(page),
                "limit": str(limit),
                "time_frame": time_frame,
                "format": "json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(self.api_url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data if isinstance(data, list) else data.get("articles", [])
                    logger.info(f"Successfully fetched {len(articles)} articles from API")
                    return articles
                else:
                    logger.error(f"API request failed: {response.status_code} - {response.text}")
                    return []
                
        except Exception as e:
            logger.error(f"Error fetching articles from API: {str(e)}", exc_info=True)
            return []
    
    async def update_cache(self) -> bool:
        logger.info("Updating news cache with fresh data")
        
        if self.cache.is_cache_stale(CRON_INTERVAL):
            articles = await self.fetch_articles()
            if articles:
                self.cache.set_articles(articles)
                return True
            return False
        
        logger.info("Cache is still fresh, skipping update")
        return True
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query = params.get("query", "")
        limit = params.get("limit", 25)
        
        hours_back = extract_time_period(query)
        if not hours_back:
            hours_back = 24
        
        logger.info(f"Executing crypto news tool (query='{query}', hours_back={hours_back}, limit={limit})")
        
        if self.cache.is_cache_stale(CRON_INTERVAL):
            logger.info("Cache is stale, updating before query")
            await self.update_cache()
        
        cached_articles = self.cache.get_articles(limit=limit, hours_back=hours_back)
        
        if not cached_articles:
            logger.warning("Cache is empty even after update attempt")
            cached_articles = await self.fetch_articles()
            if cached_articles:
                self.cache.set_articles(cached_articles)
        
        articles = []
        for article in cached_articles:
            processed = self._process_article(article)
            articles.append(processed)
            
        return {
            "articles": articles[:limit],
            "count": len(articles),
            "source": "Cache" if cached_articles else "API",
            "timestamp": datetime.now().isoformat(),
            "time_context": f"Past {hours_back} hours"
        }
    
    def _process_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "title": article.get("title"),
            "summary": article.get("summary"),
            "media": article.get("media"),
            "link": article.get("link"),
            "authors": article.get("authors"),
            "published": article.get("published"),
            "category": article.get("category"),
            "subCategory": article.get("subCategory"),
            "language": article.get("language"),
            "timeZone": article.get("timeZone")
        }
        
    def format_response(self, query: str, tool_response: Dict[str, Any]) -> Dict[str, Any]:
        hours_back = extract_time_period(query) or 24
        response = self.create_base_response(query)
        response.update({
            "answer": f"Here are the latest cryptocurrency news articles (past {hours_back} hours)",
            "context": f"Based on {tool_response.get('count', 0)} recent cryptocurrency news articles",
            "articles": tool_response.get("articles", []),
        })
        return response