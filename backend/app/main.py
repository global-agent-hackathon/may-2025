from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# It's good practice to verify necessary keys, especially if they are directly used.
# For AzureOpenAI client, the keys are usually passed to its constructor from settings.
if not os.getenv("AZURE_OPENAI_API_KEY"):  # More specific check for Azure
    print(
        "Warning: AZURE_OPENAI_API_KEY not found in environment variables. Ensure it's set for AzureOpenAI client."
    )

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Application-specific imports
from app.api.routers import (
    physics_tutor,
    chemistry_tutor,
    mathematics_tutor,
    lang_tutor,
)
from app.core.config import settings

# Imports for resources to be managed by lifespan
from agno.models.azure import (
    AzureOpenAI,
)  # Assuming this is your Azure OpenAI client class
from app.repositories.physics_tutor_repository import PhysicsTutorRepository
from app.repositories.chemistry_tutor_repository import (
    ChemistryTutorRepository,
)  # Example
from app.repositories.mathematics_tutor_repository import (
    MathematicsTutorRepository,
)  # Example
from app.repositories.lang_tutor_repository import LanguageTutorRepository  # Example
from app.core.dependencies import app_lifespan_resources


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    print("Application startup: Initializing shared resources...")

    # Initialize Azure OpenAI Client (assuming one client for all tutors, using settings)
    azure_client = AzureOpenAI(
        api_key=settings.AZURE_OPENAI_API_KEY,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_version=settings.AZURE_OPENAI_API_VERSION,
        azure_deployment=settings.AZURE_DEPLOYMENT_NAME,
    )
    app_lifespan_resources["azure_openai_client"] = azure_client
    print("Azure OpenAI client initialized.")

    # Initialize Repositories
    app_lifespan_resources["physics_repository"] = PhysicsTutorRepository()
    app_lifespan_resources["chemistry_repository"] = ChemistryTutorRepository()
    app_lifespan_resources["mathematics_repository"] = MathematicsTutorRepository()
    app_lifespan_resources["lang_repository"] = LanguageTutorRepository()
    print("Repositories initialized.")

    yield  # The application runs while the yield is active

    # --- Shutdown ---
    print("Application shutdown: Closing shared resources...")

    azure_client_to_close = app_lifespan_resources.get("azure_openai_client")
    if azure_client_to_close:
        if hasattr(azure_client_to_close, "close") and callable(
            getattr(azure_client_to_close, "close")
        ):
            azure_client_to_close.close()
            print("Azure OpenAI client closed.")

    app_lifespan_resources.clear()
    print("Shared resources cleaned up.")


app = FastAPI(
    title="AI Tutor API",
    description="API for AI-powered tutoring system",
    version="1.0.0",
    lifespan=lifespan,  # Register the lifespan context manager
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=getattr(
        settings, "CORS_ORIGINS", ["http://localhost:8081", "http://localhost:8080"]
    ),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(physics_tutor.router, prefix="/api/physics", tags=["physics"])
app.include_router(chemistry_tutor.router, prefix="/api/chemistry", tags=["chemistry"])
app.include_router(
    mathematics_tutor.router, prefix="/api/mathematics", tags=["mathematics"]
)
app.include_router(lang_tutor.router, prefix="/api/language", tags=["language"])


@app.get("/")
async def root():
    return {"message": "Welcome to AI Tutor API"}


# If you need to run this with uvicorn directly:
# import uvicorn
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
