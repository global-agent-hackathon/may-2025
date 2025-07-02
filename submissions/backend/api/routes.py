import logging

from fastapi import APIRouter, Request

from backend.schemas.schemas import ActionRequest, StatusResponse

router = APIRouter()
logger = logging.getLogger("FastAPI")


@router.get("/ping", response_model=dict, summary="Liveness check")
async def ping():
    """Test endpoint that returns pong."""
    return {"message": "pong"}


@router.post(
    "/api/videos/evaluate",
    response_model=StatusResponse,
    summary="Action for the received message",
)
async def action(payload: ActionRequest, request: Request):
    """
    Receives an HTTP request and enqueues the action.
    """
    queue = request.app.state.queue
    await queue.put(payload)
    logger.info(f"Enqueued video: {payload.videoId}")
    return StatusResponse(
        status="submitted", detail=f"Video {payload.videoId} successfully enqueued."
    )
