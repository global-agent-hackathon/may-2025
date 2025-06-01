import os
import json
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import io
import csv
from datetime import datetime

from models import (
    FormRequest, FormResponse, ChatRequest, ChatResponse, 
    AIFieldComputeRequest, AIFieldComputeResponse,
    ChartGenerationRequest, ChartGenerationResponse,
    ChartDataRequest, ChartDataResponse,
    PromptEnhancementRequest, PromptEnhancementResponse,
    MemoryEnhancementRequest, MemoryEnhancementResponse,
    # Memory models
    MemorySearchRequest, MemorySearchResponse, AddConversationMemoryRequest,
    AddFormInteractionMemoryRequest, AddUserPreferenceMemoryRequest,
    MemoryOperationResponse, UserContextRequest, UserContextResponse,
    FormHistoryRequest, FormHistoryResponse, UserPreferencesResponse
)
from services.form_service import FormService
from services.text_to_sql_service import TextToSQLService
from services.analytics_service import AnalyticsService
from services.memory_service import MemoryService
from utils.data_processors import DataProcessor
from utils.logger import get_logger
from middleware.auth import get_current_user, get_optional_user

logger = get_logger()

app = FastAPI(
    title="Flux Agent API",
    description="Professional API for intelligent form generation and data analysis with memory capabilities",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_form_service() -> FormService:
    try:
        return FormService()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_text_to_sql_service() -> TextToSQLService:
    try:
        return TextToSQLService()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_analytics_service() -> AnalyticsService:
    try:
        from core.database import DatabaseService
        database_service = DatabaseService()
        return AnalyticsService(database_service=database_service)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_memory_service() -> MemoryService:
    try:
        return MemoryService()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate", response_model=FormResponse)
async def generate_form(
    request: FormRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    form_service: FormService = Depends(get_form_service)
):
    try:
        logger.info(f"Form generation request from user {current_user['user_id']}: {request.prompt[:50]}...")
        
        # Add user context to the request
        request.user_id = current_user["user_id"]
        
        result = form_service.generate_form(
            prompt=request.prompt,
            context=request.context
        )
        
        logger.info(f"Form generated successfully for user {current_user['user_id']}")
        return FormResponse(
            title=result.title,
            description=result.description,
            fields=result.fields
        )
    except Exception as e:
        logger.error(f"Form generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compute-ai-field", response_model=AIFieldComputeResponse)
async def compute_ai_field(
    request: AIFieldComputeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    form_service: FormService = Depends(get_form_service)
):
    try:
        logger.info(f"AI field computation request from user {current_user['user_id']}")
        
        result = await form_service.compute_ai_field(
            ai_metadata_prompt=request.ai_metadata_prompt,
            form_data=request.form_data,
            field_mapping={}  # Empty mapping for now, will be improved later
        )
        
        logger.info(f"AI field computed successfully for user {current_user['user_id']}")
        return AIFieldComputeResponse(
            field_id=request.ai_field_id,
            computed_value=result,
            success=True,
            error=None
        )
    except Exception as e:
        logger.error(f"AI field computation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    text_to_sql_service: TextToSQLService = Depends(get_text_to_sql_service)
):
    try:
        logger.info(f"Chat request from user {current_user['user_id']}: {request.message[:50]}...")
        
        response = text_to_sql_service.process_message(
            message=request.message,
            form_id=request.formId,
            form_response_id=request.formResponseId,
            user_id=current_user["user_id"]
        )
        
        logger.info(f"Chat response generated successfully for user {current_user['user_id']}")
        return response
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/enhance-prompt", response_model=PromptEnhancementResponse)
async def enhance_prompt(
    request: PromptEnhancementRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    form_service: FormService = Depends(get_form_service)
):
    """Enhance a form generation prompt using AI and memory insights."""
    try:
        logger.info(f"Prompt enhancement request from user {current_user['user_id']}: {request.prompt[:50]}...")
        
        result = form_service.enhance_prompt(
            prompt=request.prompt,
            context=request.context,
            examples=request.examples
        )
        
        logger.info(f"Prompt enhanced successfully for user {current_user['user_id']}")
        return PromptEnhancementResponse(
            enhanced_prompt=result["enhanced_prompt"],
            improvements=result["improvements"],
            confidence=result["confidence"],
            reasoning=result["reasoning"]
        )
    except Exception as e:
        logger.error(f"Prompt enhancement error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/enhance-prompt-memory", response_model=MemoryEnhancementResponse)
async def enhance_prompt_with_memory(
    request: MemoryEnhancementRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    form_service: FormService = Depends(get_form_service)
):
    """Enhance a form generation prompt using memory insights and patterns."""
    try:
        logger.info(f"Memory enhancement request from user {current_user['user_id']}: {request.prompt[:50]}...")
        
        # Ensure user can only enhance using their own memories
        if request.user_id != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        result = form_service.enhance_prompt_with_memory(
            prompt=request.prompt,
            user_id=request.user_id,
            memory_context=request.memory_context,
            successful_examples=request.successful_examples
        )
        
        logger.info(f"Memory enhancement completed successfully for user {current_user['user_id']}")
        return MemoryEnhancementResponse(
            enhanced_prompt=result["enhanced_prompt"],
            improvements=result["improvements"],
            confidence=result["confidence"],
            memory_insights=result.get("memory_insights"),
            successful_patterns=result.get("successful_patterns", [])
        )
    except Exception as e:
        logger.error(f"Memory enhancement error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analytics/generate-charts", response_model=ChartGenerationResponse)
async def generate_charts(
    request: ChartGenerationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    try:
        logger.info(f"Chart generation request from user {current_user['user_id']}")
        
        result = analytics_service.generate_chart_suggestions(request)
        
        logger.info(f"Charts generated successfully for user {current_user['user_id']}")
        return result
    except Exception as e:
        logger.error(f"Chart generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analytics/chart-data", response_model=ChartDataResponse)
async def get_chart_data(
    request: ChartDataRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    try:
        logger.info(f"Chart data request from user {current_user['user_id']}")
        
        result = analytics_service.generate_chart_data(request)
        
        logger.info(f"Chart data retrieved successfully for user {current_user['user_id']}")
        return result
    except Exception as e:
        logger.error(f"Chart data error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analytics/execute-chart")
async def execute_chart(
    request: dict,
    current_user: Dict[str, Any] = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    try:
        logger.info(f"Chart execution request from user {current_user['user_id']}")
        
        result = analytics_service.execute_chart_analysis(
            request,
            user_id=current_user["user_id"]
        )
        
        if result.get("return_csv", False):
            # Return CSV data as streaming response
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=result["data"][0].keys())
            writer.writeheader()
            writer.writerows(result["data"])
            
            response = StreamingResponse(
                io.BytesIO(output.getvalue().encode()),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=chart_data.csv"}
            )
            return response
        
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Chart execution error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "flux-agent"
    }


# Memory endpoints
@app.post("/memory/search", response_model=MemorySearchResponse)
async def search_memories(
    request: MemorySearchRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Search for relevant memories."""
    try:
        logger.info(f"Memory search request from user {current_user['user_id']}: {request.query[:50]}...")
        
        # Ensure user can only search their own memories
        if request.user_id != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not memory_service.is_enabled():
            return MemorySearchResponse(memories=[], total_count=0)
        
        memories = memory_service.search_memories(
            user_id=request.user_id,
            query=request.query,
            limit=request.limit,
            memory_type=request.memory_type
        )
        
        logger.info(f"Found {len(memories)} memories for user {current_user['user_id']}")
        return MemorySearchResponse(memories=memories, total_count=len(memories))
        
    except Exception as e:
        logger.error(f"Memory search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memory/conversation", response_model=MemoryOperationResponse)
async def add_conversation_memory(
    request: AddConversationMemoryRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Add conversation memory."""
    try:
        logger.info(f"Adding conversation memory for user {current_user['user_id']}")
        
        # Ensure user can only add memories for themselves
        if request.user_id != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not memory_service.is_enabled():
            return MemoryOperationResponse(
                success=False, 
                message="Memory service is not enabled"
            )
        
        success = memory_service.add_conversation_memory(
            user_id=request.user_id,
            user_message=request.user_message,
            assistant_response=request.assistant_response,
            context=request.context
        )
        
        return MemoryOperationResponse(
            success=success,
            message="Conversation memory added successfully" if success else "Failed to add conversation memory"
        )
        
    except Exception as e:
        logger.error(f"Add conversation memory error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memory/form-interaction", response_model=MemoryOperationResponse)
async def add_form_interaction_memory(
    request: AddFormInteractionMemoryRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Add form interaction memory."""
    try:
        logger.info(f"Adding form interaction memory for user {current_user['user_id']}")
        
        # Ensure user can only add memories for themselves
        if request.user_id != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not memory_service.is_enabled():
            return MemoryOperationResponse(
                success=False, 
                message="Memory service is not enabled"
            )
        
        success = memory_service.add_form_interaction_memory(
            user_id=request.user_id,
            form_id=request.form_id,
            form_title=request.form_title,
            interaction_type=request.interaction_type,
            details=request.details
        )
        
        return MemoryOperationResponse(
            success=success,
            message="Form interaction memory added successfully" if success else "Failed to add form interaction memory"
        )
        
    except Exception as e:
        logger.error(f"Add form interaction memory error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memory/user-preference", response_model=MemoryOperationResponse)
async def add_user_preference_memory(
    request: AddUserPreferenceMemoryRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Add user preference memory."""
    try:
        logger.info(f"Adding user preference memory for user {current_user['user_id']}")
        
        # Ensure user can only add memories for themselves
        if request.user_id != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not memory_service.is_enabled():
            return MemoryOperationResponse(
                success=False, 
                message="Memory service is not enabled"
            )
        
        success = memory_service.add_user_preference_memory(
            user_id=request.user_id,
            preference_type=request.preference_type,
            preference_value=request.preference_value,
            context=request.context
        )
        
        return MemoryOperationResponse(
            success=success,
            message="User preference memory added successfully" if success else "Failed to add user preference memory"
        )
        
    except Exception as e:
        logger.error(f"Add user preference memory error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memory/user-context", response_model=UserContextResponse)
async def get_user_context(
    request: UserContextRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Get user context for a query."""
    try:
        logger.info(f"Getting user context for user {current_user['user_id']}")
        
        # Ensure user can only get their own context
        if request.user_id != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not memory_service.is_enabled():
            return UserContextResponse(context="", memories_count=0)
        
        context = memory_service.get_user_context(
            user_id=request.user_id,
            query=request.query
        )
        
        # Count memories used
        memories = memory_service.search_memories(request.user_id, request.query, limit=5)
        
        return UserContextResponse(
            context=context,
            memories_count=len(memories)
        )
        
    except Exception as e:
        logger.error(f"Get user context error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memory/form-history", response_model=FormHistoryResponse)
async def get_form_history(
    request: FormHistoryRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Get user's form interaction history."""
    try:
        logger.info(f"Getting form history for user {current_user['user_id']}")
        
        # Ensure user can only get their own history
        if request.user_id != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not memory_service.is_enabled():
            return FormHistoryResponse(interactions=[], total_count=0)
        
        interactions = memory_service.get_form_history(
            user_id=request.user_id,
            form_id=request.form_id
        )
        
        return FormHistoryResponse(
            interactions=interactions,
            total_count=len(interactions)
        )
        
    except Exception as e:
        logger.error(f"Get form history error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory/user-preferences/{user_id}", response_model=UserPreferencesResponse)
async def get_user_preferences(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Get user's stored preferences."""
    try:
        logger.info(f"Getting user preferences for user {current_user['user_id']}")
        
        # Ensure user can only get their own preferences
        if user_id != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not memory_service.is_enabled():
            return UserPreferencesResponse(preferences={}, total_count=0)
        
        preferences = memory_service.get_user_preferences(user_id)
        
        return UserPreferencesResponse(
            preferences=preferences,
            total_count=len(preferences)
        )
        
    except Exception as e:
        logger.error(f"Get user preferences error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 