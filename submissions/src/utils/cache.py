import json
import logging
import redis
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from config import CACHE_TTL

logger = logging.getLogger(__name__)

class RedisCache:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, password: int = 123):
        self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.news_key = "crypto:news:articles"
        self.last_update_key = "crypto:news:last_update"
        self.search_key_prefix = "crypto:news:search:"
        self.data_key_prefix = "crypto:data:"
        self.ttl = CACHE_TTL
        
    def set_articles(self, articles: List[Dict[str, Any]]) -> None:
        logger.info(f"Storing {len(articles)} articles in Redis cache")
        try:
            stored_count = 0
            for article in articles:
                article_id = article.get("link")
                if not article_id:
                    logger.warning("Skipping article without link")
                    continue
                
                article_hash = hashlib.md5(article_id.encode()).hexdigest()
                article_key = f"{self.news_key}:{article_hash}"
                self.redis_client.set(article_key, json.dumps(article), ex=self.ttl)
                stored_count += 1
            
            self.redis_client.set(self.last_update_key, datetime.now().isoformat())
            logger.info(f"Successfully stored {stored_count} articles in Redis cache")
        except Exception as e:
            logger.error(f"Error storing articles in Redis: {str(e)}", exc_info=True)
    
    def get_articles(self, limit: int = 100, hours_back: Optional[int] = None) -> List[Dict[str, Any]]:
        logger.info(f"Retrieving articles from Redis cache (limit={limit}, hours_back={hours_back})")
        try:
            article_keys = self.redis_client.keys(f"{self.news_key}:*")
            articles = []
            
            for key in article_keys:
                article_json = self.redis_client.get(key)
                if article_json:
                    article = json.loads(article_json)
                    
                    if hours_back is not None:
                        try:
                            pub_date = datetime.fromisoformat(article.get("published").replace("Z", "+00:00"))
                            cutoff_time = datetime.now() - timedelta(hours=hours_back)
                            if pub_date < cutoff_time:
                                continue
                        except (ValueError, TypeError, AttributeError):
                            pass
                    
                    articles.append(article)
            
            articles.sort(key=lambda x: x.get("published", ""), reverse=True)
            logger.info(f"Retrieved {len(articles)} articles from cache, returning {min(limit, len(articles))}")
            return articles[:limit]
        except Exception as e:
            logger.error(f"Error retrieving articles from Redis: {str(e)}", exc_info=True)
            return []
    
    def set_search_results(self, query: str, results: List[Dict[str, Any]]) -> None:
        logger.info(f"Storing search results for '{query}' in Redis cache")
        try:
            search_key = f"{self.search_key_prefix}{query}"
            self.redis_client.set(search_key, json.dumps(results), ex=self.ttl)
        except Exception as e:
            logger.error(f"Error storing search results in Redis: {str(e)}", exc_info=True)
    
    def get_search_results(self, query: str) -> List[Dict[str, Any]]:
        logger.info(f"Retrieving search results for '{query}' from Redis cache")
        try:
            search_key = f"{self.search_key_prefix}{query}"
            results_json = self.redis_client.get(search_key)
            
            if results_json:
                results = json.loads(results_json)
                logger.info(f"Found {len(results)} cached results for '{query}'")
                return results
            logger.info(f"No cached results found for '{query}'")
            return []
        except Exception as e:
            logger.error(f"Error retrieving search results from Redis: {str(e)}", exc_info=True)
            return []
    
    def set_data(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        logger.info(f"Storing data for key '{key}' in Redis cache")
        try:
            cache_key = f"{self.data_key_prefix}{key}"
            self.redis_client.set(cache_key, json.dumps(data), ex=ttl or self.ttl)
        except Exception as e:
            logger.error(f"Error storing data in Redis: {str(e)}", exc_info=True)
    
    def get_data(self, key: str) -> Optional[Any]:
        logger.info(f"Retrieving data for key '{key}' from Redis cache")
        try:
            cache_key = f"{self.data_key_prefix}{key}"
            data_json = self.redis_client.get(cache_key)
            
            if data_json:
                data = json.loads(data_json)
                logger.info(f"Found cached data for '{key}'")
                return data
            logger.info(f"No cached data found for '{key}'")
            return None
        except Exception as e:
            logger.error(f"Error retrieving data from Redis: {str(e)}", exc_info=True)
            return None
    
    def get_last_update_time(self) -> Optional[datetime]:
        try:
            last_update = self.redis_client.get(self.last_update_key)
            if last_update:
                return datetime.fromisoformat(last_update)
            return None
        except Exception as e:
            logger.error(f"Error getting last update time from Redis: {str(e)}", exc_info=True)
            return None
            
    def is_cache_stale(self, max_age_minutes: int) -> bool:
        last_update = self.get_last_update_time()
        if not last_update:
            logger.info("Cache appears to be empty (no last update time)")
            return True
            
        age = datetime.now() - last_update
        is_stale = age > timedelta(minutes=max_age_minutes)
        
        if is_stale:
            logger.info(f"Cache is stale (last updated {age.total_seconds()/60:.1f} minutes ago)")
        else:
            logger.info(f"Cache is fresh (last updated {age.total_seconds()/60:.1f} minutes ago)")
            
        return is_stale