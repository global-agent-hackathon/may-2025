import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.config import get_settings
from backend.schemas.schemas import VideoScoreResult, EvaluationResult
from backend.ws.connection_manager import ConnectionManager

settings = get_settings()
ws_router = APIRouter()
manager = ConnectionManager()
logger = logging.getLogger("ws")


@ws_router.websocket(settings.WS_ENDPOINT)
async def websocket_endpoint(ws: WebSocket):
    manager: ConnectionManager = ws.app.state.manager
    await manager.connect(ws)
    async with manager.lock:
        total = len(manager.active_connections)
    logger.info("Connection open. Total WebSocket clients: %d", total)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(ws)
        async with manager.lock:
            total = len(manager.active_connections)
        logger.info("Connection closed. Total WebSocket clients: %d", total)


async def send_score_to_ws(
    manager: ConnectionManager, video_id: str, evaluation_result: EvaluationResult
) -> None:
    """
    Sends the video evaluation result via WebSocket.

    Args:
        video_id (str): ID of the evaluated video
        evaluation_result (EvaluationResult): Result of the video evaluation

    Returns:
        None
    """
    logger.info(
        f"📤 Sending score for video {video_id}: {evaluation_result.overall.score}"
    )

    category_scores = {
        category.name: category.score for category in evaluation_result.categories
    }
    # Create the result object
    result = VideoScoreResult(
        video_id=video_id,
        score=evaluation_result.overall.score,
        categories=category_scores,
        evaluation_summary=evaluation_result.overall.reason,
        content_summary=evaluation_result.content_summary,
    )

    # Execute the broadcast and complete the future
    try:
        if manager is None:
            logger.info(f"Cannot send video: {video_id}")
        else:
            await manager.broadcast(result.to_dict())
    except Exception as e:
        logger.error(f"Error sending result for video {video_id}: {str(e)}")
