from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from fastapi.responses import StreamingResponse

from app.services.physics_tutor_service import PhysicsTutorService
from agno.models.azure import AzureOpenAI
from app.repositories.physics_tutor_repository import PhysicsTutorRepository
from app.core.dependencies import get_azure_openai_client, get_physics_repository


router = APIRouter()


# --- Pydantic Models ---
class SearchQuery(BaseModel):
    """
    Model for search queries in the physics tutor API.

    Attributes:
        query (str): The physics concept or topic to search for.
    """
    query: str


class SearchResponse(BaseModel):
    """
    Model for search results in the physics tutor API.

    Attributes:
        results (List[Dict[str, str]]): List of matching physics concepts with associated information.
    """
    results: List[Dict[str, str]]


class ExplanationResponse(BaseModel):
    """
    Model for detailed explanations in the physics tutor API.

    Attributes:
        content (str): The main explanation text.
        problems (str): Related practice problems.
        visuals (str): Visual aids or diagrams.
        type (str): The type of response, e.g., 'explanation' or 'error'.
    """
    content: str
    problems: str
    visuals: str
    type: str


def get_physics_tutor_service(
    client: AzureOpenAI = Depends(get_azure_openai_client),
    repo: PhysicsTutorRepository = Depends(get_physics_repository),
) -> PhysicsTutorService:
    """
    Dependency to get the PhysicsTutorService instance.

    Args:
        client (AzureOpenAI): The Azure OpenAI client.
        repo (PhysicsTutorRepository): The repository for physics tutor data.

    Returns:
        PhysicsTutorService: The physics tutor service instance.
    """
    return PhysicsTutorService(client=client)


# --- Physics Tutor API Routes ---
@router.post("/search", response_model=SearchResponse)
async def search_physics_concept(
    query: SearchQuery,
    service: PhysicsTutorService = Depends(get_physics_tutor_service),
) -> SearchResponse:
    """
    Search for a physics concept.

    Args:
        query (SearchQuery): The search query from the user.
        service (PhysicsTutorService): The physics tutor service.

    Returns:
        SearchResponse: The search results containing physics concepts.
    """
    try:
        results: List[Dict[str, str]] = await service.search_physics_concept(query.query)
        return {"results": results}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An internal error occurred: {str(e)}"
        )


@router.post("/explain", response_model=ExplanationResponse)
async def get_concept_explanation(
    query: SearchQuery,
    service: PhysicsTutorService = Depends(get_physics_tutor_service),
) -> ExplanationResponse:
    """
    Get a detailed explanation of a physics concept.

    Args:
        query (SearchQuery): The user's query containing the concept to explain.
        service (PhysicsTutorService): The physics tutor service.

    Returns:
        ExplanationResponse: A detailed explanation, including practice problems and visual aids.
    """
    try:
        explanation: ExplanationResponse = await service.get_concept_explanation(query.query)
        return explanation
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An internal error occurred: {str(e)}"
        )


@router.post("/explain/stream")
async def stream_concept_explanation(
    query: SearchQuery,
    service: PhysicsTutorService = Depends(get_physics_tutor_service),
) -> StreamingResponse:
    """
    Stream a step-by-step explanation of a physics concept.

    Args:
        query (SearchQuery): The user's query containing the concept to explain.
        service (PhysicsTutorService): The physics tutor service.

    Returns:
        StreamingResponse: A streaming response that yields JSON-formatted events in real time.
    """
    try:
        return StreamingResponse(
            service.stream_explanation(query.query),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An internal error occurred: {str(e)}"
        )
