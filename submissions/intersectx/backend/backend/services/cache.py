from datetime import datetime, timedelta
from typing import Any, Optional, TypeVar, Generic, Dict

from pydantic import BaseModel

from backend.settings import MongoConnectionDetails
from backend.database.mongo import MongoDBConnector
from backend.utils.logger import get_logger

LOG = get_logger("CacheService")

T = TypeVar("T")


class CacheEntry(BaseModel, Generic[T]):
    key: str
    data: T
    expires_at: datetime


class CacheService:
    """
    A service for caching data with MongoDB as the backend storage.
    Provides both sync and async methods for cache operations.
    """

    COLLECTION_NAME = "cache_entries"
    DEFAULT_TTL = timedelta(days=1)  # Default time-to-live is 1 day

    def __init__(self, mongo_config: MongoConnectionDetails):
        self.mongo_connector = MongoDBConnector(mongo_config)
        # Ensure indexes are created
        self._setup_indexes()

    def _setup_indexes(self):
        """Setup necessary indexes for the cache collection"""
        from backend.database.mongo import MongoIndexSpec

        # Check if collection exists and has our indexes
        collection = self.mongo_connector.get_collection(self.COLLECTION_NAME)
        existing_indexes = collection.index_information()

        # If the key_index already exists, we don't need to create indexes
        if "key_index" in existing_indexes:
            LOG.debug("Cache collection indexes already exist")
            return

        LOG.info(f"Creating indexes for collection: {self.COLLECTION_NAME}")
        indexes = [
            MongoIndexSpec(keys=[("key", 1)], name="key_index", unique=True),
            MongoIndexSpec(keys=[("expires_at", 1)], name="expiry_index"),
        ]
        self.mongo_connector.create_indexes(self.COLLECTION_NAME, indexes)

    def _generate_key(
        self, service_name: str, method_name: str, args: Dict[str, Any]
    ) -> str:
        """Generate a unique cache key based on service, method and arguments"""
        args_str = "&".join(f"{k}={v}" for k, v in sorted(args.items()))
        return f"{service_name}:{method_name}:{args_str}"

    def _serialize_for_mongodb(self, data: Any) -> Any:
        """Convert data to MongoDB-compatible format"""
        if data is None:
            return None

        # Handle Pydantic models
        if hasattr(data, "model_dump"):
            try:
                return data.model_dump()
            except Exception as e:
                LOG.error(f"Error serializing Pydantic model: {e}")
                # Fallback to dict
                try:
                    return dict(data)
                except Exception:
                    LOG.error(
                        f"Failed to convert Pydantic model to dict for {type(data)}"
                    )
                    # Return just the string representation as a last resort
                    return str(data)

        # Handle lists
        elif isinstance(data, list):
            return [self._serialize_for_mongodb(item) for item in data]

        # Handle dictionaries
        elif isinstance(data, dict):
            return {k: self._serialize_for_mongodb(v) for k, v in data.items()}

        # Handle datetimes
        elif hasattr(data, "isoformat"):
            return data.isoformat()

        # Handle any objects with __dict__
        elif hasattr(data, "__dict__"):
            try:
                return self._serialize_for_mongodb(data.__dict__)
            except Exception as e:
                LOG.error(f"Error serializing object with __dict__: {e}")
                return str(data)

        # Handle other types that MongoDB can store directly
        return data

    def get(
        self, service_name: str, method_name: str, args: Dict[str, Any]
    ) -> Optional[Any]:
        """Get cached data if it exists and is not expired"""
        key = self._generate_key(service_name, method_name, args)

        # Query for unexpired cache entry
        now = datetime.utcnow()
        query = {"key": key, "expires_at": {"$gt": now}}

        results = self.mongo_connector.query(self.COLLECTION_NAME, query)
        if results and len(results) > 0:
            LOG.info(f"Cache hit for {key}")
            return results[0]["data"]

        LOG.info(f"Cache miss for {key}")
        return None

    def set(
        self,
        service_name: str,
        method_name: str,
        args: Dict[str, Any],
        data: Any,
        ttl: Optional[timedelta] = None,
    ) -> None:
        """Store data in cache with expiration time"""
        key = self._generate_key(service_name, method_name, args)
        expires_at = datetime.utcnow() + (ttl or self.DEFAULT_TTL)

        # Serialize data for MongoDB
        serialized_data = self._serialize_for_mongodb(data)

        # Upsert the cache entry
        query_filter = {"key": key}
        update_operation = {"$set": {"data": serialized_data, "expires_at": expires_at}}

        self.mongo_connector.update_records(
            self.COLLECTION_NAME, query_filter, update_operation
        )
        LOG.info(f"Cached data for {key}, expires at {expires_at}")

    def invalidate(
        self, service_name: str, method_name: str, args: Dict[str, Any]
    ) -> None:
        """Invalidate a specific cache entry"""
        key = self._generate_key(service_name, method_name, args)
        self.mongo_connector.delete_records(self.COLLECTION_NAME, {"key": key})
        LOG.info(f"Invalidated cache for {key}")

    def clear_all(self) -> None:
        """Clear all cache entries"""
        self.mongo_connector.delete_records(self.COLLECTION_NAME, {})
        LOG.info("Cleared all cache entries")

    def clear_expired(self) -> None:
        """Clear all expired cache entries"""
        now = datetime.utcnow()
        self.mongo_connector.delete_records(
            self.COLLECTION_NAME, {"expires_at": {"$lt": now}}
        )
        LOG.info("Cleared expired cache entries")

    # Async methods
    async def aget(
        self, service_name: str, method_name: str, args: Dict[str, Any]
    ) -> Optional[Any]:
        """Async version of get"""
        key = self._generate_key(service_name, method_name, args)

        # Query for unexpired cache entry
        now = datetime.utcnow()
        query = {"key": key, "expires_at": {"$gt": now}}

        results = await self.mongo_connector.aquery(self.COLLECTION_NAME, query)
        if results and len(results) > 0:
            LOG.info(f"Cache hit for {key}")
            return results[0]["data"]

        LOG.info(f"Cache miss for {key}")
        return None

    async def aset(
        self,
        service_name: str,
        method_name: str,
        args: Dict[str, Any],
        data: Any,
        ttl: Optional[timedelta] = None,
    ) -> None:
        """Async version of set"""
        key = self._generate_key(service_name, method_name, args)
        expires_at = datetime.utcnow() + (ttl or self.DEFAULT_TTL)

        # Serialize data for MongoDB
        serialized_data = self._serialize_for_mongodb(data)

        # Upsert the cache entry
        collection = await self.mongo_connector.aget_collection(self.COLLECTION_NAME)
        await collection.update_one(
            {"key": key},
            {"$set": {"data": serialized_data, "expires_at": expires_at}},
            upsert=True,
        )
        LOG.info(f"Cached data for {key}, expires at {expires_at}")

    async def ainvalidate(
        self, service_name: str, method_name: str, args: Dict[str, Any]
    ) -> None:
        """Async version of invalidate"""
        key = self._generate_key(service_name, method_name, args)
        await self.mongo_connector.adelete_records(self.COLLECTION_NAME, {"key": key})
        LOG.info(f"Invalidated cache for {key}")

    async def aclear_all(self) -> None:
        """Async version of clear_all"""
        await self.mongo_connector.adelete_records(self.COLLECTION_NAME, {})
        LOG.info("Cleared all cache entries")

    async def aclear_expired(self) -> None:
        """Async version of clear_expired"""
        now = datetime.utcnow()
        await self.mongo_connector.adelete_records(
            self.COLLECTION_NAME, {"expires_at": {"$lt": now}}
        )
        LOG.info("Cleared expired cache entries")
