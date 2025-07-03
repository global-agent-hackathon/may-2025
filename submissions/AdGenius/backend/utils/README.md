# AdGenius Utils Module

This module provides utility functions for the AdGenius backend application, including logging, configuration management, and middleware components.

## Logger

The logger utility provides a consistent, configurable logging system across the application.

### Basic Usage

```python
from utils import get_logger

# Create a simple logger
logger = get_logger("my_module")
logger.info("This is an information message")
logger.error("An error occurred", exc_info=True)  # Include exception traceback

# Create a detailed logger with file output
logger = get_logger(
    "detailed_module", 
    level="debug",
    detailed=True,          # Include filename and line numbers
    log_to_file=True,       # Save to file
    log_dir="./app_logs"    # Directory for log files
)
```

### Contextual Logging

Add contextual information to logs:

```python
from utils import get_logger, with_context

logger = get_logger("request_handler")

# Add user and request info to all logs in this block
with with_context(logger, {"user_id": "123", "request_id": "abc-def"}):
    logger.info("Processing user request")  # Will include user_id and request_id
    logger.debug("Request details", extra={"payload": "..."})
```

### Configuration

Logger behavior can be controlled through environment variables:

- `LOG_LEVEL`: Set logging level (debug, info, warning, error, critical)
- `LOG_FORMAT`: Custom format string
- `LOG_DATE_FORMAT`: Custom date format
- `LOG_DIR`: Directory for log files when `log_to_file=True`
- `LOG_TO_FILE`: Enable/disable file logging ("true"/"false") 

## Configuration Management

The config module provides a centralized configuration system:

```python
from utils import config, is_production

# Access configuration values
api_key = config.some_api_key

# Use environment helpers
if is_production():
    # Do production-specific things
else:
    # Do development-specific things
```

Configuration is loaded from environment variables and `.env` files.

## Request Logging Middleware

Middleware for automatic request/response logging:

```python
from fastapi import FastAPI
from utils import RequestLoggingMiddleware

app = FastAPI()
app.add_middleware(
    RequestLoggingMiddleware,
    exclude_paths=["/health", "/metrics"],  # Skip noisy endpoints
    log_headers=True  # Include headers in logs (dev only)
)
```

Features:
- Automatic timing of requests
- Request ID generation and tracking
- Contextual logging
- HTTP method and status code logging
- Path and query parameter logging

## Performance Helpers

The example module includes performance monitoring helpers:

```python
from utils.example import log_performance

@log_performance
async def my_function():
    # Function execution time will be logged
    ...
```
