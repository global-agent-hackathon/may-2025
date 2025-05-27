# app/core/dependencies.py

from fastapi import HTTPException, Depends
from typing import Dict, Any  # Generic type for the resources dictionary

# --- Shared Resources Dictionary ---
# This dictionary will be populated by the lifespan manager in main.py
# and accessed by dependency providers in routers.
app_lifespan_resources: Dict[str, Any] = {}

# --- Import Types for Dependency Functions ---
# These are just type hints, so they don't cause circular imports
# if the actual classes are defined elsewhere.
# Forward references as strings can also be used if needed for complex types.
from agno.models.azure import AzureOpenAI  # Or your specific client type
from app.repositories.physics_tutor_repository import PhysicsTutorRepository
from app.repositories.chemistry_tutor_repository import (
    ChemistryTutorRepository,
)  # Example
from app.repositories.mathematics_tutor_repository import (
    MathematicsTutorRepository,
)  # Example
from app.repositories.lang_tutor_repository import LanguageTutorRepository  # Example

# --- Generic Dependency Providers (can be specialized in routers or kept here) ---


def get_azure_openai_client() -> AzureOpenAI:
    client = app_lifespan_resources.get("azure_openai_client")
    if not client:
        raise HTTPException(
            status_code=503, detail="Azure OpenAI client is not available."
        )
    return client


def get_physics_repository() -> PhysicsTutorRepository:
    repo = app_lifespan_resources.get("physics_repository")
    if not repo:
        raise HTTPException(status_code=503, detail="Physics repository not available.")
    return repo


def get_chemistry_repository() -> ChemistryTutorRepository:
    repo = app_lifespan_resources.get("chemistry_repository")
    if not repo:
        raise HTTPException(
            status_code=503, detail="Chemistry repository not available."
        )
    return repo


def get_mathematics_repository() -> MathematicsTutorRepository:
    repo = app_lifespan_resources.get("mathematics_repository")
    if not repo:
        raise HTTPException(
            status_code=503, detail="Mathematics repository not available."
        )
    return repo


def get_lang_repository() -> LanguageTutorRepository:
    repo = app_lifespan_resources.get("lang_repository")
    if not repo:
        raise HTTPException(
            status_code=503, detail="Language repository not available."
        )
    return repo


# You can also define service getters here if they are simple,
# or keep them in the respective router files if they have more specific logic.
# For example, if PhysicsTutorService is always the same:
# from app.services.physics_tutor_service import PhysicsTutorService
# def get_physics_tutor_service_dependency(
#     client: AzureOpenAI = Depends(get_azure_openai_client),
#     repo: PhysicsTutorRepository = Depends(get_physics_repository)
# ) -> PhysicsTutorService:
#     return PhysicsTutorService(client=client, repository=repo)
