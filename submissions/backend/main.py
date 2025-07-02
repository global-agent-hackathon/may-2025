import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router as api_router
from backend.config import get_settings
import logging

from backend.queue.video_queue import lifespan
from backend.ws.websocket import ws_router

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME, debug=settings.DEBUG, version="1.0.0", lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(api_router, tags=["Utility"])
app.include_router(ws_router)
# Logging configuration
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(levelname)s | %(asctime)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info(f"Starting application at: http://{settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_config=None,
    )
