from datetime import datetime

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import chat router and initialization function
from chat_assistant.endpoints import chat_router
from chat_assistant.endpoints.common import setup_chat_db
from google_oauth import init_db

# Import Google OAuth module
from google_oauth import router as auth_router

# Import utilities
from utils import RequestLoggingMiddleware, config, get_logger, is_production
from utils.db import ensure_sqlite_dir_exists

# Import application dependencies

# Initialize logger
logger = get_logger("adgenius.app")

# Initialize FastAPI app
app = FastAPI(
    title="AdGenius Backend",
    description="AI-powered advertising platform API",
    version="0.1.0",
    docs_url=None if is_production() else "/docs",
    redoc_url=None if is_production() else "/redoc",
)

logger.info("Starting AdGenius backend application")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
app.add_middleware(
    RequestLoggingMiddleware,
    exclude_paths=["/health", "/metrics", "/docs", "/redoc", "/openapi.json"],
    log_headers=not is_production(),  # Log headers only in non-production environments
)

# API Router
api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(chat_router)
app.include_router(api_router)


# API endpoints
@app.get("/")
def read_root():
    logger.debug("Root endpoint called")
    return {"message": "Welcome to AdGenius API"}


@app.get("/api/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0",
    }


@app.on_event("startup")
async def startup_db_client():
    """Initialize connections and databases on startup"""
    logger.info("Initializing application services")

    ensure_sqlite_dir_exists(config.database_url)

    try:
        # Initialize the chat database
        logger.info("Initializing chat database...")
        await setup_chat_db()
        logger.info("Chat database initialized successfully")

        # Initialize the user database
        logger.info("Initializing user database...")
        await init_db()
        logger.info("User database initialization complete")

        # Log configuration (excluding sensitive information)
        safe_config = {
            k: v
            for k, v in config.to_dict().items()
            if not any(secret in k.lower() for secret in ["secret", "password", "key"])
        }
        logger.debug(f"Application configuration: {safe_config}")

    except Exception as e:
        logger.critical(f"Failed to initialize application: {str(e)}", exc_info=True)
        raise

    logger.info("Application startup complete")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
