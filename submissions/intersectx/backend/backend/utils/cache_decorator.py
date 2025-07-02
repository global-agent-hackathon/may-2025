import functools
import inspect
from datetime import timedelta
from typing import Any, Callable, Dict, Optional, TypeVar, cast

from backend.services.cache import CacheService

T = TypeVar("T")


def cacheable(ttl: Optional[timedelta] = None):
    """
    A decorator for caching service method results.

    Args:
        ttl: Optional time-to-live for the cache entry. If not provided, defaults to 1 day.

    Usage:
        @cacheable()
        def my_method(self, arg1, arg2, ...):
            ...

        @cacheable(ttl=timedelta(hours=1))
        async def my_async_method(self, arg1, arg2, ...):
            ...
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        is_async = inspect.iscoroutinefunction(func)

        @functools.wraps(func)
        async def async_wrapper(self, *args, **kwargs) -> T:
            # Get the cache service from the service instance
            if not hasattr(self, "cache_service") or not isinstance(
                self.cache_service, CacheService
            ):
                # If no cache service is available, just execute the method
                return await func(self, *args, **kwargs)

            cache_service = cast(CacheService, self.cache_service)

            # Get service name from the class
            service_name = self.__class__.__name__

            # Get method name
            method_name = func.__name__

            # Create a dictionary of arguments
            # Exclude 'self' from args
            arg_names = list(inspect.signature(func).parameters.keys())[1:]
            arg_dict: Dict[str, Any] = {}

            # Add positional arguments
            for i, arg_name in enumerate(arg_names):
                if i < len(args):
                    # If the argument is provided positionally
                    arg_dict[arg_name] = str(args[i])
                elif arg_name in kwargs:
                    # If the argument is provided as a keyword
                    arg_dict[arg_name] = str(kwargs[arg_name])

            # Add keyword arguments that weren't already captured
            for kw, value in kwargs.items():
                if kw not in arg_dict:
                    arg_dict[kw] = str(value)

            # Try to get from cache first
            cached_result = await cache_service.aget(
                service_name, method_name, arg_dict
            )
            if cached_result is not None:
                return cached_result

            # Execute the method if not cached
            result = await func(self, *args, **kwargs)

            # Cache the result
            await cache_service.aset(service_name, method_name, arg_dict, result, ttl)

            return result

        @functools.wraps(func)
        def sync_wrapper(self, *args, **kwargs) -> T:
            # Get the cache service from the service instance
            if not hasattr(self, "cache_service") or not isinstance(
                self.cache_service, CacheService
            ):
                # If no cache service is available, just execute the method
                return func(self, *args, **kwargs)

            cache_service = cast(CacheService, self.cache_service)

            # Get service name from the class
            service_name = self.__class__.__name__

            # Get method name
            method_name = func.__name__

            # Create a dictionary of arguments
            # Exclude 'self' from args
            arg_names = list(inspect.signature(func).parameters.keys())[1:]
            arg_dict: Dict[str, Any] = {}

            # Add positional arguments
            for i, arg_name in enumerate(arg_names):
                if i < len(args):
                    # If the argument is provided positionally
                    arg_dict[arg_name] = str(args[i])
                elif arg_name in kwargs:
                    # If the argument is provided as a keyword
                    arg_dict[arg_name] = str(kwargs[arg_name])

            # Add keyword arguments that weren't already captured
            for kw, value in kwargs.items():
                if kw not in arg_dict:
                    arg_dict[kw] = str(value)

            # Try to get from cache first
            cached_result = cache_service.get(service_name, method_name, arg_dict)
            if cached_result is not None:
                return cached_result

            # Execute the method if not cached
            result = func(self, *args, **kwargs)

            # Cache the result
            cache_service.set(service_name, method_name, arg_dict, result, ttl)

            return result

        if is_async:
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
