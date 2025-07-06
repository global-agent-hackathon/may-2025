import logging
import os
import httpx
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..utils.cache import RedisCache
from ..models import CryptoNewsResponse
from .base_tool import BaseTool

logger = logging.getLogger(__name__)

class CryptoSearchTool(BaseTool):
    name = "crypto_search"
    description = "Search for cryptocurrency news articles by keyword. Use this when looking for specific topics or cryptocurrencies."
    
    def __init__(self, redis_cache: RedisCache):
        super().__init__()
        self.cache = redis_cache
        self.api_key = os.getenv("RAPIDAPI_KEY", "")
        self.api_host = os.getenv("RAPIDAPI_HOST", "crypto-news51.p.rapidapi.com")
        self.api_url = "https://crypto-news51.p.rapidapi.com/api/v1/crypto/articles/search"
    
    async def search_articles(self, keywords: str, page: int = 1, limit: int = 10, time_frame: str = "24h") -> List[Dict[str, Any]]:
        logger.info(f"Searching crypto news articles: keywords='{keywords}', page={page}, limit={limit}")
        
        try:
            if not self.api_key:
                logger.error("RAPIDAPI_KEY is not set")
                return []
            
            headers = {
                "x-rapidapi-host": self.api_host,
                "x-rapidapi-key": self.api_key
            }
            
            params = {
                "title_keywords": keywords,
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
                    
                    logger.info(f"Successfully found {len(articles)} articles for '{keywords}'")
                    self.cache.set_search_results(keywords, articles)
                    
                    return articles
                else:
                    logger.error(f"API search request failed: {response.status_code} - {response.text}")
                    return []
                
        except Exception as e:
            logger.error(f"Error searching articles: {str(e)}", exc_info=True)
            return []
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query = params.get("query", "")
        limit = params.get("limit", 10)
        
        keywords = query.lower().strip()
        
        logger.info(f"Executing crypto search tool (keywords='{keywords}', limit={limit})")
        
        if not keywords:
            logger.warning("No keywords provided for search")
            return {
                "error": "Keywords parameter is required",
                "articles": [],
                "count": 0,
                "keywords": keywords
            }
        
        cached_results = self.cache.get_search_results(keywords)
        
        if not cached_results:
            logger.info(f"No cached results for '{keywords}', fetching from API")
            cached_results = await self.search_articles(keywords, limit=limit)
        
        articles = []
        for article in cached_results:
            processed = self._process_article(article)
            articles.append(processed)
            
        return {
            "keywords": keywords,
            "articles": articles[:limit],
            "count": len(articles),
            "source": "Cache" if cached_results else "API",
            "timestamp": datetime.now().isoformat()
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
        keywords = tool_response.get("keywords", "")
        response = self.create_base_response(query)
        response.update({
            "answer": f"Here are search results for '{keywords}' in cryptocurrency news",
            "context": f"Based on {tool_response.get('count', 0)} articles matching '{keywords}'",
            "articles": tool_response.get("articles", []),
        })
        return response