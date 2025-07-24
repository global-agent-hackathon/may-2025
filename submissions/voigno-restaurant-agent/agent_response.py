import asyncio

from loguru import logger

from pipecat.frames.frames import (
    CancelFrame,
    EmulateUserStartedSpeakingFrame,
    EmulateUserStoppedSpeakingFrame,
    EndFrame,
    Frame,
    InterimTranscriptionFrame,
    LLMMessagesFrame,
    StartFrame,
    TranscriptionFrame,
    UserStartedSpeakingFrame,
    UserStoppedSpeakingFrame,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor


class AgentMessageAggregator(FrameProcessor):
    """
    Message aggregator for AgentLLM that processes and aggregates transcriptions from user speech.

    This aggregator collects transcriptions between VAD events (UserStartedSpeakingFrame and
    UserStoppedSpeakingFrame) and sends the aggregated message to the AgentLLM service for processing.
    Unlike context-based aggregators, this doesn't maintain a full conversation context.

    The agent will handle its own conversation context internally, so we just need to pass
    the aggregated user message as a simple message.
    """

    def __init__(
        self,
        aggregation_timeout: float = 1.0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._aggregation_timeout = aggregation_timeout

        # Aggregation state
        self._aggregation = ""
        self._seen_interim_results = False
        self._user_speaking = False
        self._emulating_vad = False
        self._waiting_for_aggregation = False

        # Event and task for timeout-based aggregation
        self._aggregation_event = asyncio.Event()
        self._aggregation_task = None

    def reset(self):
        """Reset the aggregation state."""
        self._aggregation = ""
        self._seen_interim_results = False
        self._waiting_for_aggregation = False

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if isinstance(frame, StartFrame):
            # Push StartFrame before any setup
            await self.push_frame(frame, direction)
            await self._start(frame)
        elif isinstance(frame, EndFrame):
            # Push EndFrame before cleanup
            await self.push_frame(frame, direction)
            await self._stop(frame)
        elif isinstance(frame, CancelFrame):
            await self._cancel(frame)
            await self.push_frame(frame, direction)
        elif isinstance(frame, UserStartedSpeakingFrame):
            await self._handle_user_started_speaking(frame)
            await self.push_frame(frame, direction)
        elif isinstance(frame, UserStoppedSpeakingFrame):
            await self._handle_user_stopped_speaking(frame)
            await self.push_frame(frame, direction)
        elif isinstance(frame, TranscriptionFrame):
            await self._handle_transcription(frame)
        elif isinstance(frame, InterimTranscriptionFrame):
            await self._handle_interim_transcription(frame)
        else:
            await self.push_frame(frame, direction)

    async def push_aggregation(self):
        """Push the aggregated message downstream as an LLMMessagesFrame."""
        if len(self._aggregation) > 0:
            aggregation = self._aggregation

            # Reset before pushing downstream
            self.reset()

            # Create a message with the aggregated text in OpenAI compatible format
            # This ensures compatibility with both string content and content array formats
            message = {
                "role": "user",
                "content": [{"type": "text", "text": aggregation}],
            }

            logger.debug(f"{self} Pushing aggregated message: {message}")
            await self.push_frame(LLMMessagesFrame(messages=[message]))

    async def _start(self, frame: StartFrame):
        self._create_aggregation_task()

    async def _stop(self, frame: EndFrame):
        await self._cancel_aggregation_task()

    async def _cancel(self, frame: CancelFrame):
        await self._cancel_aggregation_task()

    async def _handle_user_started_speaking(self, frame: UserStartedSpeakingFrame):
        self._user_speaking = True
        self._waiting_for_aggregation = True

    async def _handle_user_stopped_speaking(self, frame: UserStoppedSpeakingFrame):
        self._user_speaking = False
        # If the last thing we saw is not an interim transcription, push the aggregation
        if not self._seen_interim_results:
            await self.push_aggregation()

        # Pass the frame downstream
        await self.push_frame(frame)

    async def _handle_transcription(self, frame: TranscriptionFrame):
        text = frame.text

        # Skip empty text for aggregation, but still pass the frame
        if not text.strip():
            await self.push_frame(frame)
            return

        self._aggregation += f" {text}" if self._aggregation else text

        # Reset interim results flag
        self._seen_interim_results = False

        # Reset aggregation timer
        self._aggregation_event.set()

        # Pass the transcription frame downstream so other processors can see it
        await self.push_frame(frame)

    async def _handle_interim_transcription(self, frame: InterimTranscriptionFrame):
        self._seen_interim_results = True

        # Pass the interim transcription frame downstream
        await self.push_frame(frame)

    def _create_aggregation_task(self):
        if not self._aggregation_task:
            self._aggregation_task = self.create_task(self._aggregation_task_handler())

    async def _cancel_aggregation_task(self):
        if self._aggregation_task:
            await self.cancel_task(self._aggregation_task)
            self._aggregation_task = None

    async def _aggregation_task_handler(self):
        while True:
            try:
                await asyncio.wait_for(
                    self._aggregation_event.wait(), self._aggregation_timeout
                )
                await self._maybe_push_bot_interruption()
            except asyncio.TimeoutError:
                if not self._user_speaking:
                    await self.push_aggregation()

                # If we are emulating VAD, send a stopped speaking frame
                if self._emulating_vad:
                    await self.push_frame(
                        EmulateUserStoppedSpeakingFrame(), FrameDirection.UPSTREAM
                    )
                    self._emulating_vad = False
            finally:
                self._aggregation_event.clear()

    async def _maybe_push_bot_interruption(self):
        """
        Handle cases where we receive transcription without VAD detection
        (e.g., when the user whispers a short utterance)
        """
        if not self._user_speaking and not self._waiting_for_aggregation:
            await self.push_frame(
                EmulateUserStartedSpeakingFrame(), FrameDirection.UPSTREAM
            )
            self._emulating_vad = True
