from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime, timezone

from core.dependencies import get_current_user_session
from .mail_agents import QueryAgent, WritingAgent, DailySummaryAgent

router = APIRouter(prefix="/api/agents", tags=["AI Agents"])

query_agent_instance = QueryAgent()
writing_agent_instance = WritingAgent()
daily_summary_agent_instance = DailySummaryAgent()

class ChatQueryRequest(BaseModel):
    query: str
    history: Optional[List[Dict[str, str]]] = None 

class ChatQueryResponse(BaseModel):
    answer: str

class DraftEmailRequest(BaseModel):
    recipient_to: str
    user_prompt: str
    current_draft_content: Optional[str] = None

class DraftEmailResponse(BaseModel):
    subject: str
    body: str
    
class DailySummaryResponse(BaseModel):
    summary: str
    generated_at: datetime

@router.post("/query/chat", response_model=ChatQueryResponse)
async def handle_chat_query(
    request_body: ChatQueryRequest,
    session_data: dict = Depends(get_current_user_session)
):
    user_id_str = str(session_data.get("user_id"))
    if not user_id_str:
        raise HTTPException(status_code=401, detail="User not authenticated")

    try:
        answer = await query_agent_instance.answer_query(
            user_id=user_id_str,
            query=request_body.query,
            conversation_history=request_body.history
        )
        return ChatQueryResponse(answer=answer)
    except Exception as e:
        print(f"Error in /query/chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to process your query.")

@router.post("/writing/draft", response_model=DraftEmailResponse)
async def handle_draft_email(
    request_body: DraftEmailRequest,
    session_data: dict = Depends(get_current_user_session)
):
    user_id_str = str(session_data.get("user_id"))
    if not user_id_str:
        raise HTTPException(status_code=401, detail="User not authenticated")

    try:
        draft = await writing_agent_instance.draft_email(
            user_id=user_id_str,
            recipient_to=request_body.recipient_to,
            user_prompt=request_body.user_prompt,
            current_draft_content=request_body.current_draft_content
        )
        return DraftEmailResponse(subject=draft.get("subject", ""), body=draft.get("body", ""))
    except Exception as e:
        print(f"Error in /writing/draft endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate email draft.")
    
@router.get("/summary/daily", response_model=DailySummaryResponse)
async def get_daily_mail_summary(
    session_data: dict = Depends(get_current_user_session)
):
    user_id_str = str(session_data.get("user_id"))
    if not user_id_str:
        raise HTTPException(status_code=401, detail="User not authenticated")
    try:
        summary_text = await daily_summary_agent_instance.get_daily_summary(user_id=user_id_str)
        return DailySummaryResponse(summary=summary_text, generated_at=datetime.now(timezone.utc))
    except Exception as e:
        print(f"Error in /summary/daily endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate daily summary.")