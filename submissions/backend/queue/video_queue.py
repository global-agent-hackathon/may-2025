import asyncio
import logging
from contextlib import asynccontextmanager
from typing import List

from backend.agent.agent import run_agent
from backend.config import get_settings
from backend.schemas.schemas import ActionRequest
from backend.ws.connection_manager import ConnectionManager

settings = get_settings()
logger = logging.getLogger("queue")


# Global queue for ActionRequest
async def worker(queue: asyncio.Queue, manager: ConnectionManager, worker_id: str):
    while True:
        try:
            payload: ActionRequest = await queue.get()
            logger.info(f"[W{worker_id}] ⏳ Processing video: {payload.videoId}")
            await run_agent(
                payload.videoId, payload.categories, payload.customPrompts, manager
            )
            logger.info(f"[W{worker_id}] ✅ Successfully processed {payload.videoId!r}")
        except Exception as e:
            logger.error(f"Error processing {payload.videoId}: {e}", exc_info=True)
        finally:
            queue.task_done()
            size_after = queue.qsize()
            logger.info(f"[W{worker_id}] ← {size_after} tasks remaining in the queue")


@asynccontextmanager
async def lifespan(app):
    # Initialize queue and manager in app state
    queue: asyncio.Queue = asyncio.Queue()
    manager = ConnectionManager()
    app.state.queue = queue
    app.state.manager = manager

    # Start the workers
    tasks: List[asyncio.Task] = []
    for _ in range(settings.WORKERS):
        task = asyncio.create_task(worker(queue, manager, "worker_" + str(_)))
        # Register a callback for uncaught exception logging
        task.add_done_callback(lambda t: _log_task_exc(t, logger))
        tasks.append(task)

    yield
    for task in tasks:
        task.cancel()
    # Ensure complete cancellation
    await asyncio.gather(*tasks, return_exceptions=True)


def _log_task_exc(task: asyncio.Task, logger):
    if task.cancelled():
        return
    if task.exception():
        logger.error("Error in process_video_with_agent:", exc_info=task.exception())
