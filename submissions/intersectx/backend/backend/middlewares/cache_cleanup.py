import asyncio
import time
from datetime import datetime, timedelta
from typing import Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from backend.services.cache import CacheService
from backend.utils.logger import get_logger

LOG = get_logger()


class CacheCleanupMiddleware(BaseHTTPMiddleware):
    """
    Middleware that periodically cleans up expired cache entries.
    """

    def __init__(
        self,
        app: ASGIApp,
        cache_service: CacheService,
        cleanup_interval: timedelta = timedelta(hours=1),
    ):
        super().__init__(app)
        self.cache_service = cache_service
        self.cleanup_interval = cleanup_interval
        self.last_cleanup = datetime.utcnow()
        LOG.info(
            f"Cache cleanup middleware initialized with interval: {cleanup_interval}"
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check if it's time to clean up
        now = datetime.utcnow()
        if now - self.last_cleanup > self.cleanup_interval:
            # Run cleanup in background to avoid blocking request handling
            asyncio.create_task(self._cleanup_expired_cache())
            self.last_cleanup = now

        # Continue processing the request
        return await call_next(request)

    async def _cleanup_expired_cache(self):
        """Clean up expired cache entries"""
        try:
            LOG.info("Starting cache cleanup...")
            start_time = time.time()
            await self.cache_service.aclear_expired()
            elapsed = time.time() - start_time
            LOG.info(f"Cache cleanup completed in {elapsed:.2f} seconds")
        except Exception as e:
            LOG.error(f"Error during cache cleanup: {e}")


def setup_cache_cleanup_middleware(app: FastAPI, cache_service: CacheService):
    """
    Set up the cache cleanup middleware for the FastAPI application.
    """
    app.add_middleware(
        CacheCleanupMiddleware,
        cache_service=cache_service,
        cleanup_interval=timedelta(hours=1),
    )
    LOG.info("Cache cleanup middleware added to the application")
