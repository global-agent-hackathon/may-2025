from agno.agent import Agent, AgentMemory
from agno.tools.mcp import MCPTools
from backend.settings import LLMConfig, MongoConnectionDetails
from backend.utils.llm import get_model
from backend.utils.logger import get_logger
from agno.storage.mongodb import MongoDbStorage
from backend.database.mongo import MongoDBConnector
from backend.models.requests.chat import SendMessageRequest
from backend.models.response.chat import (
    ChatThreadWithMessages,
    MessageResponse,
    ThreadSummary,
    LastMessage,
)
from backend.models.base.chat import MessageMetadata, AgnoMessage
from agno.run.response import RunResponse
from fastapi.responses import StreamingResponse
from typing import List, Optional, Union, AsyncGenerator
import uuid
import json
from textwrap import dedent
import asyncio
from datetime import datetime

LOG = get_logger("Chat Service")


class ChatService:
    def __init__(
        self,
        llm_config: LLMConfig,
        db_config: MongoConnectionDetails,
        mcp_url: str,
        history_runs: int = 10,
        timeout: int = 300,
    ):
        self.llm_config = llm_config
        self.db_config = db_config
        self.mcp_url = mcp_url
        self.history_runs = history_runs
        self.timeout = timeout

        self.storage = MongoDbStorage(
            collection_name="chat_agent",
            db_name=db_config.dbname,
            db_url=db_config.get_connection_string(),
            mode="agent",
        )
        self.memory = AgentMemory(
            create_user_memories=True,
            storage=self.storage,
            update_user_memories_after_run=True,
            create_session_summaries=True,
            update_session_summaries_after_run=True,
        )
        self.mongo = MongoDBConnector(db_config)

    @staticmethod
    def system_agent_prompt() -> str:
        return dedent(
            """You are a specialized search-based AI assistant powered by the Sonar endpoint. Your purpose is to retrieve, synthesize, and present relevant information from Venture Insights' databases in response to user queries about companies and markets."""
        )

    @staticmethod
    def system_instructions() -> str:
        return dedent(f"""
The current date is {datetime.now().isoformat()}.
## Purpose and Role

You leverage search capabilities to find and deliver accurate information about companies, markets, and industry trends. Your goal is to provide users with relevant insights to support their business research and decision-making.

## Response Approach

- Interpret user queries to identify the key information they need about companies or markets
- Provide concise, focused answers that directly address the user's question
- Present information in a clear, structured format that highlights key points
- Balance detailed analysis with accessibility for users of varying expertise levels
- When appropriate, suggest additional related information that might be valuable

## Conversation Style

- Maintain a professional, helpful tone
- Ask clarifying questions when needed to better understand the user's information needs
- Be decisive when providing recommendations or analyses
- Show genuine interest in helping users find the specific market insights they need
- Keep responses focused and avoid unnecessary elaboration
- when appropriate, use emojis to enhance the user experience if necessary

## Guidelines for Using Venture Insights Tools

- Use company_name for company-specific analyses
- Include domain, region, or industry parameters to narrow analysis
- Provide start_date and end_date for trend analyses
- Include categories or products parameters when available
- Identify which tool suits the query best
- Combine tools for comprehensive insights
- Do not Include the Iframe url as in response

Always prioritize delivering accurate, relevant information from Venture Insights' knowledge base in a way that's most helpful to the user's specific request.
""")

    async def _create_agent(
        self, user_id: str, session_id: str, mcp_tools, markdown: bool = False
    ) -> Agent:
        return Agent(
            session_id=session_id,
            agent_id=session_id,
            user_id=user_id,
            model=get_model(self.llm_config),
            tools=[mcp_tools],
            markdown=markdown,
            description=self.system_agent_prompt(),
            instructions=self.system_instructions(),
            storage=self.storage,
            memory=self.memory,
        )

    async def process_query(
        self,
        user_message: str,
        thread_id: str,
        user_id: str,
        stream: bool = False,
        markdown: bool = False,
    ) -> RunResponse:
        """Process a user query using the MCP tools."""
        async with MCPTools(
            url=self.mcp_url, transport="streamable-http", timeout_seconds=self.timeout
        ) as mcp_tools:
            agent = await self._create_agent(
                user_id=user_id,
                session_id=thread_id,
                markdown=markdown,
                mcp_tools=mcp_tools,
            )
            return await agent.arun(user_message, stream=stream)

    async def run_interactive(
        self,
        user_message: str,
        thread_id: str,
        user_id: str,
        stream: bool = True,
        markdown: bool = False,
    ) -> None:
        """Run the agent with a streamed response."""
        async with MCPTools(
            url=self.mcp_url, transport="streamable-http", timeout_seconds=self.timeout
        ) as mcp_tools:
            agent = await self._create_agent(
                user_id=user_id,
                session_id=thread_id,
                markdown=markdown,
                mcp_tools=mcp_tools,
            )
            await agent.aprint_response(user_message, stream=stream)

    async def _format_thread(self, thread: dict) -> ChatThreadWithMessages:
        runs = thread.get("memory", {}).get("messages", [])
        messages = [
            m for m in runs if m.get("role") not in ("system") and m.get("content")
        ]
        return ChatThreadWithMessages(
            id=thread["session_id"],
            updated_at=thread.get("updated_at"),
            created_by=thread.get("user_id"),
            messages=[
                MessageResponse(
                    content=m["content"],
                    sender=m["role"],
                    timestamp=m.get("created_at"),
                    user_id=thread.get("user_id"),
                    metadata=m.get("metadata"),
                )
                for m in messages
            ],
        )

    async def _format_thread_summary(self, thread: dict) -> ThreadSummary:
        runs = thread.get("memory", {}).get("messages", [])
        messages = [
            m for m in runs if m.get("role") not in ("system") and m.get("content")
        ]

        # Get the last message if any
        last_message = None
        if messages:
            last_msg = messages[-1]
            last_message = LastMessage(
                content=last_msg["content"],
                sender=last_msg["role"],
                timestamp=last_msg.get("created_at", datetime.now()),
                user_id=thread.get("user_id"),
            )

        return ThreadSummary(
            id=thread["session_id"],
            created_at=thread.get("created_at"),
            updated_at=thread.get("updated_at"),
            created_by=thread.get("user_id"),
            last_message=last_message,
            message_count=len(messages),
        )

    async def get_threads(
        self,
        limit: int = 10,
        offset: int = 0,
        user_id: Optional[str] = None,
        sort_by: str = "updated_at",
        sort_order: str = "desc",
    ) -> List[ThreadSummary]:
        query = {"user_id": user_id} if user_id else {}

        # Fetch threads without sorting
        threads = await self.mongo.aquery("chat_agent", query)

        # Manual sorting
        sort_field = (
            sort_by if sort_by in ["created_at", "updated_at"] else "updated_at"
        )
        reverse_sort = sort_order.lower() == "desc"

        # Sort the threads (handle None values by placing them at the end)
        sorted_threads = sorted(
            threads, key=lambda t: t.get(sort_field, datetime.min), reverse=reverse_sort
        )

        # Apply pagination after sorting
        paginated_threads = sorted_threads[offset : offset + limit]

        return [await self._format_thread_summary(t) for t in paginated_threads]

    async def get_thread(self, thread_id: str, user_id: str) -> ChatThreadWithMessages:
        threads = await self.mongo.aquery(
            "chat_agent", {"session_id": thread_id, "user_id": user_id}
        )
        LOG.debug(f"Found {len(threads)} threads for user {user_id}")
        if not threads:
            return ChatThreadWithMessages(messages=[], id=thread_id)
        return await self._format_thread(threads[0])

    async def delete_thread(self, thread_id: str, user_id: str) -> bool:
        await self.mongo.adelete_records(
            "chat_agent", {"session_id": thread_id, "user_id": user_id}
        )
        return True

    async def add_message(
        self,
        thread_id: str,
        message: SendMessageRequest,
        stream: bool = False,
    ) -> Union[MessageResponse, StreamingResponse]:
        """Add a message to a chat thread, streaming if required."""
        if not stream:
            run = await self.process_query(
                user_message=message.content,
                thread_id=thread_id,
                user_id=message.user_id,
                stream=False,
            )
            return MessageResponse(
                id=str(uuid.uuid4()),
                content=run.content,
                sender="assistant",
                metadata=MessageMetadata(
                    tools=[t.to_dict() for t in run.tools],
                    formatted_tool_calls=run.formatted_tool_calls,
                    citations=run.citations,
                    messages=[
                        AgnoMessage(role=m.role, content=m.content)
                        for m in run.messages
                        if m.role not in ("system")
                    ],
                    model=run.model,
                ),
                user_id=message.user_id,
                user_name=message.user_name,
            )

        async def stream_gen() -> AsyncGenerator[str, None]:
            async with MCPTools(
                url=self.mcp_url,
                transport="streamable-http",
                timeout_seconds=self.timeout,
            ) as mcp_tools:
                agent = await self._create_agent(
                    user_id=message.user_id, session_id=thread_id, mcp_tools=mcp_tools
                )
                stream_resp = await agent.arun(message.content, stream=True)
                async for chunk in stream_resp:
                    text = getattr(chunk, "content", str(chunk))
                    yield f"data: {json.dumps({'content': text})}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(
            stream_gen(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            },
        )


if __name__ == "__main__":
    from dotenv import load_dotenv
    from backend.settings import get_app_settings

    async def main():
        load_dotenv()

        app_settings = get_app_settings()

        agent = ChatService(
            llm_config=app_settings.llm_config,
            db_config=app_settings.db_config,
            mcp_url=app_settings.mcp_url,
        )

        await agent.run_interactive(
            user_message="What's the revenue analysis for Datagenie AI?",
            thread_id="test_thread_id_2",
            user_id="test_user_id_2",
            stream=True,
        )

    asyncio.run(main())
