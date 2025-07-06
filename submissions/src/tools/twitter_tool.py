import logging
import os
import httpx
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from ..models import CryptoNewsResponse, TweetItem
from ..utils.cache import RedisCache
from .base_tool import BaseTool

logger = logging.getLogger(__name__)

class TwitterTool(BaseTool):
    name = "twitter"
    description = "Get cryptocurrency-related data from Twitter/X. Use this for real-time social media insights if twitter/X is specifically mentioned."
    
    MAX_TWEET_AGE_DAYS = 30
    DEFAULT_TWEET_LIMIT = 10
    CACHE_TTL = 60 * 60  # 1 hour cache TTL
    
    def __init__(self, redis_cache: RedisCache):
        super().__init__()
        self.cache = redis_cache
        self.api_key = os.getenv("TWEETSCOUT_API_KEY", "")
        self.api_url = "https://api.tweetscout.io/v2/search-tweets"
        self.cache_prefix = "crypto:twitter:search:"
    
    async def search_tweets(self, query: str, limit: int = DEFAULT_TWEET_LIMIT, order: str = "popular", next_cursor: Optional[str] = None) -> Dict[str, Any]:
        logger.info(f"Searching tweets with query: '{query}', limit={limit}, order={order}, cursor={next_cursor}")
        
        try:
            if not self.api_key:
                logger.error("TWEETSCOUT_API_KEY is not set")
                return {"tweets": [], "next_cursor": None, "error": "API key not configured"}
            
            enhanced_query = query
            if not any(term in query.lower() for term in ["crypto", "bitcoin", "btc", "eth"]):
                enhanced_query = f"{query} crypto"
                logger.info(f"Enhanced query to '{enhanced_query}' for better crypto relevance")
            
            headers = {
                "Accept": "application/json",
                "ApiKey": self.api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "query": enhanced_query,
                "order": order
            }
            
            if next_cursor:
                payload["next_cursor"] = next_cursor
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        self.api_url,
                        headers=headers,
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        tweets = data.get("tweets", [])
                        next_cursor = data.get("next_cursor")
                        
                        logger.info(f"Successfully fetched {len(tweets)} tweets for query '{enhanced_query}'")
                        
                        return {
                            "tweets": tweets,
                            "next_cursor": next_cursor
                        }
                    elif response.status_code == 403 and "limit exceeded" in response.text.lower():
                        logger.error("Twitter API rate limit exceeded")
                        return {
                            "tweets": [],
                            "next_cursor": None,
                            "error": "Rate limit exceeded, try again later"
                        }
                    else:
                        logger.error(f"TweetScout API request failed: {response.status_code} - {response.text}")
                        return {
                            "tweets": [],
                            "next_cursor": None,
                            "error": f"API request failed with status {response.status_code}"
                        }
            except httpx.RequestError as e:
                logger.error(f"Network error when calling Twitter API: {str(e)}")
                return {
                    "tweets": [],
                    "next_cursor": None,
                    "error": "Network error when connecting to Twitter API"
                }
                
        except Exception as e:
            logger.error(f"Error searching tweets: {str(e)}", exc_info=True)
            return {
                "tweets": [],
                "next_cursor": None,
                "error": f"Unexpected error: {str(e)}"
            }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query = params.get("query", "cryptocurrency")
        limit = params.get("limit", self.DEFAULT_TWEET_LIMIT)
        order = params.get("order", "popular")
        
        logger.info(f"Executing Twitter tool (query='{query}', limit={limit})")
        
        clean_query = query.lower().strip()
        cache_key = f"{self.cache_prefix}{clean_query}:{order}"
        cached_data = self.cache.get_data(cache_key)
        
        tweets = []
        source = "Cache"
        error_message = None
        next_cursor = None
        
        if cached_data and self._is_cache_fresh(cached_data.get("timestamp")):
            logger.info(f"Using cached tweets for query '{clean_query}'")
            tweets = cached_data.get("tweets", [])
            next_cursor = cached_data.get("next_cursor")
        else:
            logger.info(f"No fresh cache for query '{clean_query}', fetching from API")
            search_result = await self.search_tweets(clean_query, limit=limit * 2, order=order)
            tweets = search_result.get("tweets", [])
            next_cursor = search_result.get("next_cursor")
            error_message = search_result.get("error")
            
            if tweets:
                self.cache.set_data(cache_key, {
                    "tweets": tweets,
                    "next_cursor": next_cursor,
                    "timestamp": datetime.now().isoformat()
                }, self.CACHE_TTL)
                source = "API"
            elif error_message:
                logger.warning(f"Twitter API error: {error_message}")
                fallback_key = f"{self.cache_prefix}cryptocurrency:{order}"
                fallback_data = self.cache.get_data(fallback_key)
                if fallback_data:
                    tweets = fallback_data.get("tweets", [])
                    next_cursor = fallback_data.get("next_cursor")
                    logger.info(f"Found {len(tweets)} fallback tweets from cache")
                    source = "Fallback Cache"
            else:
                source = "API (No Results)"
        
        cutoff_date = datetime.now() - timedelta(days=self.MAX_TWEET_AGE_DAYS)
        filtered_tweets = []
        
        for tweet in tweets:
            try:
                tweet_date = self._parse_tweet_date(tweet.get("created_at", ""))
                if tweet_date and tweet_date >= cutoff_date:
                    filtered_tweets.append(tweet)
            except Exception:
                filtered_tweets.append(tweet) 
        
        processed_tweets = [self._process_tweet(tweet) for tweet in filtered_tweets]
        processed_tweets.sort(key=lambda t: self._parse_tweet_date(t.get("created_at", "")) or datetime.min, reverse=True)
        
        result = {
            "query": query,
            "tweets": processed_tweets[:limit],
            "count": len(processed_tweets),
            "source": source,
            "next_cursor": next_cursor,
            "timestamp": datetime.now().isoformat()
        }
        
        if error_message and len(processed_tweets) == 0:
            result["error"] = error_message
        
        return result
    
    def _process_tweet(self, tweet: Dict[str, Any]) -> Dict[str, Any]:
        user = tweet.get("user", {})
        
        media = []
        links = []
        entities = tweet.get("entities", [])
        if isinstance(entities, list):
            for entity in entities:
                entity_type = entity.get("type", "")
                entity_link = entity.get("link", "")
                
                if entity_type and entity_link:
                    if entity_type.lower() in ["photo", "video", "gif", "image"]:
                        media.append(entity_link)
                    else:
                        links.append(entity_link)
        
        is_retweet = "retweeted_status" in tweet and tweet.get("retweeted_status")
        is_quote = tweet.get("is_quote_status", False) and "quoted_status" in tweet and tweet.get("quoted_status")
        
        text = tweet.get("full_text", "")
        
        if is_retweet:
            rt_user = tweet.get("retweeted_status", {}).get("user", {}).get("screen_name", "unknown")
            rt_text = tweet.get("retweeted_status", {}).get("full_text", "")
            text = f"RT @{rt_user}: {rt_text}"
        elif is_quote:
            quote_user = tweet.get("quoted_status", {}).get("user", {}).get("screen_name", "unknown")
            quote_text = tweet.get("quoted_status", {}).get("full_text", "")
            text = f"{text}\n\nQuoting @{quote_user}: {quote_text}"
        
        return {
            "id": tweet.get("id_str", ""),
            "text": text,
            "author": user.get("screen_name", ""),
            "author_name": user.get("name", ""),
            "created_at": tweet.get("created_at", ""),
            "likes": tweet.get("favorite_count", 0),
            "retweets": tweet.get("retweet_count", 0),
            "replies": tweet.get("reply_count", 0),
            "views": tweet.get("view_count", 0),
            "avatar": user.get("avatar", ""),
            "media": media,
            "links": links,
            "is_retweet": is_retweet,
            "is_quote": is_quote,
            "conversation_id": tweet.get("conversation_id_str", "")
        }
    
    def _is_cache_fresh(self, timestamp_str: Optional[str]) -> bool:
        if not timestamp_str:
            return False
        
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            age = datetime.now() - timestamp
            return age < timedelta(seconds=self.CACHE_TTL)
        except (ValueError, TypeError):
            return False
    
    def _parse_tweet_date(self, date_str: str) -> Optional[datetime]:
        if not date_str:
            return None
        
        try:
            return datetime.strptime(date_str, "%a %b %d %H:%M:%S %z %Y")
        except ValueError:
            try:
                return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            except ValueError:
                logger.warning(f"Could not parse tweet date: {date_str}")
                return None
    
    def _convert_to_model_tweets(self, tweets: List[Dict[str, Any]]) -> List[TweetItem]:
        return [
            TweetItem(
                id=tweet.get("id", ""),
                text=tweet.get("text", ""),
                author=tweet.get("author", ""),
                created_at=tweet.get("created_at", ""),
                likes=tweet.get("likes", 0),
                retweets=tweet.get("retweets", 0)
            )
            for tweet in tweets
        ]
        
    def format_response(self, query: str, tool_response: Dict[str, Any]) -> Dict[str, Any]:
        tweets = tool_response.get("tweets", [])
        tweet_count = len(tweets)
        
        processed_tweets = []
        for tweet in tweets:
            if isinstance(tweet, dict):
                media_urls = tweet.get("media", [])
                
                processed_tweet = {
                    "title": f"Tweet by @{tweet.get('author', 'unknown')}",
                    "summary": tweet.get("text", ""),
                    "link": f"https://twitter.com/{tweet.get('author', 'unknown')}/status/{tweet.get('id', '')}",
                    "media": media_urls,
                    "authors": [{"name": f"@{tweet.get('author', 'unknown')}"}],
                    "published": tweet.get("created_at", ""),
                    "category": "Social Media",
                    "subCategory": "Twitter"
                }
                processed_tweets.append(processed_tweet)
        
        response = self.create_base_response(query)
        
        if tweet_count > 0:
            answer = f"Found {tweet_count} relevant tweets about cryptocurrency"
            context = f"Based on Twitter activity related to your query: '{query}'"
        else:
            answer = "No relevant tweets found for your query"
            context = "Twitter data is limited for this topic"
            
        response.update({
            "answer": answer,
            "context": context,
            "articles": processed_tweets,
        })
        
        return response