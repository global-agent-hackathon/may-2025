"""
AdGenius Chat Agent powered by Agno and AWS Bedrock
"""

import json
from typing import AsyncGenerator

from agno.reasoning.step import ReasoningStep, ReasoningSteps
from agno.run.response import RunEvent
from sqlalchemy.ext.asyncio import AsyncSession

# Custom modules
from agents import create_agentic_team
from utils import get_logger

# Configure logging
logger = get_logger("chat_agent")


class ChatAgent:
    """Chat agent implementation using Agno with AWS Bedrock"""

    def __init__(self, session: AsyncSession, conversation_id: str, user_id: str):
        """Initialize the chat agent with a conversation ID"""
        self.conversation_id = conversation_id
        self.user_id = user_id
        self.agent = create_agentic_team(
            db_session=session,
            user_id=user_id,
            conversation_id=conversation_id,
            debug_mode=True,
        )
        # self.agent = create_assist_agent(
        #     db_session=session,
        #     user_id=user_id,
        #     conversation_id=conversation_id,
        #     debug_mode=True,
        # )

    async def process_message(self, message: str) -> AsyncGenerator[str, None]:
        """Process a user message and stream the response with detailed Agno events.

        Args:
            message: The user message to process
        """
        try:
            # Stream the response using Agno's async API
            agno_response_stream = await self.agent.arun(
                message,
                stream=True,
                stream_intermediate_steps=True,
            )

            async for chunk in agno_response_stream:
                # print(
                #     "--------------------------------------------------------------------------"
                # )
                # print(self.agent.session_state)
                # print(
                #     "--------------------------------------------------------------------------"
                # )

                event_type = chunk.event
                done_flag = False

                if isinstance(chunk.content, ReasoningStep) or isinstance(
                    chunk.content, ReasoningSteps
                ):
                    chunk.content = None

                chunk_data_json = chunk.to_json()
                chunk_data = json.loads(chunk_data_json)
                # Remove unwanted keys if present
                for key in ["messages", "extra_data", "citations"]:
                    chunk_data.pop(key, None)

                payload = {
                    "event_type": event_type,
                    "data": chunk_data,
                    "done": done_flag,
                }

                if (
                    event_type == RunEvent.run_completed.value
                    or event_type == RunEvent.run_cancelled.value
                ):
                    payload["done"] = True

                elif event_type == RunEvent.run_error.value:
                    payload["done"] = True
                    logger.error(
                        f"Agno run error in stream: {chunk.content} - Event data: {chunk_data}"
                    )

                yield json.dumps(payload)

        except Exception as e:
            # Log the error
            logger.error(
                f"Error processing message stream with Agno: {str(e)}", exc_info=True
            )

            # Yield a final error event to the frontend so the client knows the
            # stream terminated due to an error instead of silently failing.
            final_error_payload = {
                "event_type": RunEvent.run_error.value,
                "data": {
                    "error_message": str(e),
                    "details": "Critical error during Agno stream processing.",
                },
                "done": True,
            }

            yield json.dumps(final_error_payload)
