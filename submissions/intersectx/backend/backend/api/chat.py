from fastapi import APIRouter, Depends, Path, Query, HTTPException
from fastapi_utils.cbv import cbv

from backend.dependencies import get_chat_service, get_user
from backend.models.base.users import User
from backend.models.requests.chat import (
    SendMessageRequest,
)
from backend.models.response.chat import (
    ChatThreadWithMessages,
    MessageResponse,
    ThreadSummary,
)
from backend.services.chat import ChatService
from backend.utils.logger import get_logger
import uuid
from typing import List

chat_router = APIRouter(prefix="/chat", tags=["chat"])
LOG = get_logger("Chat API")


@cbv(chat_router)
class ChatAPI:
    chat_service: ChatService = Depends(get_chat_service)
    user: User = Depends(get_user)

    @chat_router.get("/threads", response_model=List[ThreadSummary])
    async def get_threads(
        self,
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        user_id: str = Query(None, description="User ID"),
        sort_by: str = Query(
            "updated_at", description="Field to sort by (updated_at or created_at)"
        ),
        sort_order: str = Query("desc", description="Sort order (asc or desc)"),
    ) -> List[ThreadSummary]:
        if not user_id and self.user:
            LOG.debug(
                f"User ID not provided, using user ID from session: {self.user.user_id}"
            )
            user_id = self.user.user_id

        return await self.chat_service.get_threads(
            limit, offset, user_id, sort_by=sort_by, sort_order=sort_order
        )

    @chat_router.post("/threads", response_model=dict)
    async def create_thread(self) -> dict:
        LOG.debug("Creating a new thread")
        return {"thread_id": str(uuid.uuid4())}

    @chat_router.get("/threads/{thread_id}", response_model=ChatThreadWithMessages)
    async def get_thread(
        self,
        thread_id: str = Path(...),
        user_id: str = Query(None, description="User ID"),
    ) -> ChatThreadWithMessages:
        LOG.debug(f"Getting thread {thread_id} for user {user_id}")
        if not user_id and self.user:
            user_id = self.user.user_id
            LOG.debug(
                f"User ID not provided, using user ID from session: {self.user.user_id}"
            )

        try:
            return await self.chat_service.get_thread(thread_id, user_id)
        except HTTPException as e:
            LOG.warning(f"Error retrieving thread {thread_id}: {e.detail}")
            raise e

    @chat_router.delete("/threads/{thread_id}")
    async def delete_thread(
        self,
        thread_id: str = Path(...),
        user_id: str = Query(None, description="User ID"),
    ) -> dict:
        LOG.debug(f"Deleting thread {thread_id} for user {user_id}")

        if not user_id and self.user:
            user_id = self.user.user_id
            LOG.debug(
                f"User ID not provided, using user ID from session: {self.user.user_id}"
            )

        success = await self.chat_service.delete_thread(thread_id, user_id)
        return {"success": success}

    @chat_router.post("/threads/{thread_id}/messages", response_model=MessageResponse)
    async def send_message(
        self,
        request: SendMessageRequest,
        thread_id: str = Path(...),
        stream: bool = False,
    ) -> MessageResponse:
        LOG.debug(f"Sending message to thread {thread_id} and payload is {request}")

        # Add user info if not provided in request
        if not request.user_id and self.user:
            request.user_id = self.user.user_id
            LOG.debug(
                f"User ID not provided, using user ID from session: {self.user.user_id}"
            )

        return await self.chat_service.add_message(thread_id, request, stream)
