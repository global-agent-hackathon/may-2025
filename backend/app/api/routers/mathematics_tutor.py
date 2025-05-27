from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict
from app.services.mathematics_tutor_service import MathematicsTutorService
from agno.models.azure import AzureOpenAI
from app.repositories.mathematics_tutor_repository import MathematicsTutorRepository
from app.core.dependencies import get_azure_openai_client, get_mathematics_repository

router = APIRouter()


# --- Pydantic Models ---
class SearchQuery(BaseModel):
    """
    Model for search queries in the mathematics tutor API.
    
    Attributes:
        query (str): The query string for searching mathematical concepts.
    """
    query: str


class SearchResponse(BaseModel):
    """
    Model for search results in the mathematics tutor API.
    
    Attributes:
        results (List[Dict[str, str]]): A list of dictionaries containing search results.
    """
    results: List[Dict[str, str]]


class ExplanationResponse(BaseModel):
    """
    Model for detailed explanations in the mathematics tutor API.
    
    Attributes:
        content (str): The explanation content.
        practice (str): Practice problems related to the explanation.
        type (str): The type of the response, typically 'explanation' or 'error'.
    """
    content: str
    practice: str
    type: str


def get_mathematics_tutor_service(
    client: AzureOpenAI = Depends(get_azure_openai_client),
    repo: MathematicsTutorRepository = Depends(get_mathematics_repository),
) -> MathematicsTutorService:
    """
    Dependency to get the MathematicsTutorService instance.
    
    Args:
        client (AzureOpenAI): The Azure OpenAI client instance.
        repo (MathematicsTutorRepository): The repository for mathematics tutor data.
    
    Returns:
        MathematicsTutorService: The service instance for mathematics tutoring.
    """
    return MathematicsTutorService(client=client, repository=repo)


# --- Mathematics Tutor API Routes ---
@router.post("/search", response_model=SearchResponse)
async def search_mathematics_concept(
    query: SearchQuery,
    service: MathematicsTutorService = Depends(get_mathematics_tutor_service),
) -> SearchResponse:
    """
    Search for a mathematics concept.
    
    Args:
        query (SearchQuery): The search query for the concept.
        service (MathematicsTutorService): The mathematics tutor service.
    
    Returns:
        SearchResponse: The search results as a list of dictionaries.
    """
    try:
        results: List[Dict[str, str]] = await service.search_mathematics_concept(query.query)
        return {"results": results}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An internal error occurred: {str(e)}"
        )


@router.post("/explain", response_model=ExplanationResponse)
async def get_concept_explanation(
    query: SearchQuery,
    service: MathematicsTutorService = Depends(get_mathematics_tutor_service),
) -> ExplanationResponse:
    """
    Get a detailed explanation of a mathematics concept.
    
    Args:
        query (SearchQuery): The user's mathematics question.
        service (MathematicsTutorService): The mathematics tutor service.
    
    Returns:
        ExplanationResponse: A detailed explanation with practice problems.
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
    service: MathematicsTutorService = Depends(get_mathematics_tutor_service),
) -> StreamingResponse:
    """
    Stream a step-by-step explanation of a mathematics concept.
    
    Args:
        query (SearchQuery): The user's mathematics question.
        service (MathematicsTutorService): The mathematics tutor service.
    
    Returns:
        StreamingResponse: A streaming response that yields JSON-formatted events.
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
