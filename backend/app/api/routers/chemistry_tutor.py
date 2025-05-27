from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from fastapi.responses import StreamingResponse

# --- Application-specific imports ---
from app.services.chemistry_tutor_service import ChemistryTutorService
from agno.models.azure import AzureOpenAI
from app.repositories.chemistry_tutor_repository import ChemistryTutorRepository
from app.core.dependencies import get_azure_openai_client, get_chemistry_repository

router = APIRouter()


# --- Pydantic Models ---
class SearchQuery(BaseModel):
    """
    Model for search queries in the chemistry tutor API.
    
    Attributes:
        query (str): The user's search string.
    """
    query: str


class SearchResponse(BaseModel):
    """
    Model for search results in the chemistry tutor API.
    
    Attributes:
        results (List[Dict[str, str]]): A list of dictionaries containing search results.
    """
    results: List[Dict[str, str]]


class ExplanationResponse(BaseModel):
    """
    Model for detailed explanations in the chemistry tutor API.
    
    Attributes:
        content (str): The main explanation text.
        problems (str): Example problems related to the concept.
        visuals (str): Visual descriptions or diagrams.
        type (str): The response type (e.g., 'explanation', 'error').
    """
    content: str
    problems: str
    visuals: str
    type: str


def get_chemistry_tutor_service(
    client: AzureOpenAI = Depends(get_azure_openai_client),
    repo: ChemistryTutorRepository = Depends(get_chemistry_repository),
) -> ChemistryTutorService:
    """
    Dependency to get the ChemistryTutorService instance.
    
    Args:
        client (AzureOpenAI): The Azure OpenAI client.
        repo (ChemistryTutorRepository): The repository for chemistry tutor data.
        
    Returns:
        ChemistryTutorService: An instance of the ChemistryTutorService.
    """
    return ChemistryTutorService(client=client, repository=repo)


# --- Chemistry Tutor API Routes ---

@router.post("/search", response_model=SearchResponse)
async def search_chemistry_concept(
    query: SearchQuery,
    service: ChemistryTutorService = Depends(get_chemistry_tutor_service),
) -> SearchResponse:
    """
    Search for a chemistry concept.
    
    Args:
        query (SearchQuery): The search query containing the concept to search for.
        service (ChemistryTutorService): The chemistry tutor service dependency.
        
    Returns:
        SearchResponse: A response containing the search results.
    """
    try:
        results: List[Dict[str, str]] = await service.search_chemistry_concept(query.query)
        return {"results": results}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An internal error occurred: {str(e)}"
        )


@router.post("/explain", response_model=ExplanationResponse)
async def get_concept_explanation(
    query: SearchQuery,
    service: ChemistryTutorService = Depends(get_chemistry_tutor_service),
) -> ExplanationResponse:
    """
    Get a detailed explanation of a chemistry concept.
    
    Args:
        query (SearchQuery): The user's chemistry question.
        service (ChemistryTutorService): The chemistry tutor service dependency.
        
    Returns:
        ExplanationResponse: A detailed explanation of the concept.
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
    service: ChemistryTutorService = Depends(get_chemistry_tutor_service),
) -> StreamingResponse:
    """
    Stream a step-by-step explanation of a chemistry concept.
    
    Args:
        query (SearchQuery): The user's chemistry question.
        service (ChemistryTutorService): The chemistry tutor service dependency.
        
    Returns:
        StreamingResponse: A streaming response that yields explanations in real-time.
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
