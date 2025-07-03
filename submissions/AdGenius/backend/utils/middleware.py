import time
import uuid
from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .logger import get_logger

# Create a logger for HTTP requests
request_logger = get_logger("adgenius.http")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""

    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: Optional[list] = None,
        log_headers: bool = False,
    ):
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/health", "/metrics"]
        self.log_headers = log_headers

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip logging for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Generate request ID
        request_id = str(uuid.uuid4())

        # Extract client IP
        forwarded = request.headers.get("X-Forwarded-For")
        client_ip = (
            forwarded.split(",")[0]
            if forwarded
            else (request.client.host if request.client else "unknown")
        )

        # Create context for logging
        context = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client_ip": client_ip,
        }

        # Add request ID header to response
        start_time = time.time()

        # Log request start
        request_logger.info(
            f"Request started: {request.method} {request.url.path}", extra=context
        )

        # Log headers if enabled
        if self.log_headers and request_logger.isEnabledFor(10):  # DEBUG level
            headers = dict(request.headers.items())
            # Remove sensitive headers
            for sensitive in ["authorization", "cookie"]:
                if sensitive in headers:
                    headers[sensitive] = "[REDACTED]"
            request_logger.debug(f"Request headers: {headers}", extra=context)

        try:
            # Process the request
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            context["duration_ms"] = round(duration_ms, 2)  # store as float
            context["status_code"] = response.status_code
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            # Ensure all header values are strings
            response.headers["X-Duration-MS"] = f"{context['duration_ms']:.2f}"

            # Log based on status code
            if 500 <= response.status_code < 600:
                request_logger.error(
                    f"Request failed: {request.method} {request.url.path} - {response.status_code}",
                    extra=context,
                )
            elif 400 <= response.status_code < 500:
                request_logger.warning(
                    f"Request error: {request.method} {request.url.path} - {response.status_code}",
                    extra=context,
                )
            else:
                request_logger.info(
                    f"Request completed: {request.method} {request.url.path} - {response.status_code} ({context['duration_ms']:.2f}ms)",
                    extra=context,
                )

            return response

        except Exception as e:
            # Log unhandled exceptions
            duration_ms = (time.time() - start_time) * 1000
            context["duration_ms"] = round(duration_ms, 2)  # store as float
            context["error"] = str(e)

            request_logger.exception(
                f"Unhandled exception during request: {request.method} {request.url.path}",
                extra=context,
            )
            raise
