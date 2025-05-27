from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from agno.models.azure import AzureOpenAI
from app.services.lang_tutor_service import LanguageTutorService
from app.core.dependencies import get_azure_openai_client
from typing import Dict

router: APIRouter = APIRouter()


class Query(BaseModel):
    """
    Model for queries in the language tutor API.
    
    Attributes:
        query (str): The text or topic to inquire about.
        language_code (str): The target language code (default: 'en').
    """
    query: str
    language_code: str = "en"


class DialogueRequest(BaseModel):
    """
    Model for dialogue requests in the language tutor API.
    
    Attributes:
        topic (str): The topic for the conversation.
        language_code (str): The target language code.
        agree (bool): Whether the user agrees to generate the dialogue.
    """
    topic: str
    language_code: str
    agree: bool


def get_language_tutor_service(
    client: AzureOpenAI = Depends(get_azure_openai_client),
    language_code: str = "en"
) -> LanguageTutorService:
    """
    Dependency to get the LanguageTutorService instance.
    
    Args:
        client (AzureOpenAI): The Azure OpenAI client.
        language_code (str): The language code for the tutor service, default is "en".
    
    Returns:
        LanguageTutorService: An instance of the LanguageTutorService.
    """
    return LanguageTutorService(client=client, language_code=language_code)


@router.post("/explain/stream")
async def stream_explanation(
    query: Query,
    client: AzureOpenAI = Depends(get_azure_openai_client)
) -> StreamingResponse:
    """
    Stream explanations for a given query in the specified language.
    
    Args:
        query (Query): The query containing the text to explain and the language code.
        client (AzureOpenAI): The Azure OpenAI client dependency.
    
    Returns:
        StreamingResponse: A streaming response that yields explanations in real-time.
    """
    try:
        language_service: LanguageTutorService = LanguageTutorService(
            client=client, language_code=query.language_code
        )
        return StreamingResponse(
            language_service.get_tutoring_session_intro(query.query),
            media_type="text/event-stream",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dialogue")
async def create_dialogue(
    request: DialogueRequest,
    client: AzureOpenAI = Depends(get_azure_openai_client)
) -> Dict[str, str]:
    """
    Create a dialogue for language practice based on the user's agreement.
    
    Args:
        request (DialogueRequest): The request containing the topic, language code, and agreement.
        client (AzureOpenAI): The Azure OpenAI client dependency.
    
    Returns:
        Dict[str, str]: A dictionary containing the dialogue content or an info message.
    """
    try:
        language_service: LanguageTutorService = LanguageTutorService(
            client=client, language_code=request.language_code
        )
        if request.agree:
            dialogue: Dict[str, str] = await language_service.create_dialogue(request.topic)
            return dialogue
        else:
            return {
                "type": "info",
                "content": "No problem! You can always practice later.",
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
