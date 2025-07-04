from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware

from core.config import settings
from database.session import init_db
from auth.router import router as auth_router
from gmail_sync.router import router as gmail_sync_router
from mails.router import router as mails_router
from agents.router import router as agents_router
from users.router import router as user_settings_router

from core.weaviate_client import get_weaviate_client as init_weaviate

@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    print("Initializing database...")
    init_db()
    print("Database initialization complete.")
    print("Initializing Weaviate client...")
    init_weaviate()
    print("Weaviate client initialization complete.")
    yield
    print("Application shutdown.")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    SessionMiddleware, 
    secret_key=settings.SESSION_SECRET_KEY,
    same_site="lax",
    https_only=False
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, tags=["Authentication"])
app.include_router(gmail_sync_router, tags=["Gmail Sync"])
app.include_router(mails_router, tags=["Mails"])
app.include_router(agents_router)
app.include_router(user_settings_router)