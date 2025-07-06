from textwrap import dedent
from agno.agent import Agent
from agno.knowledge.pdf_url import AgentKnowledge
from agno.vectordb.qdrant import Qdrant
from config import settings
from agno.models.openai import OpenAIChat

vector_db = Qdrant(
    api_key=settings.QDRANT_API_KEY,
    collection=settings.QDRANT_COLLECTION_NAME,
    url=settings.QDRANT_URL,
)

knowledge_base = AgentKnowledge(vector_db=vector_db)

description = dedent(
    """\
    "You are an intelligent assistant designed to extract, summarize, and communicate key insights from meeting transcripts. "
    "Your purpose is to deliver clear, concise, and actionable information that helps users quickly understand the most important points discussed."
"""
)

instructions = dedent(
    """\
    "1. Response Quality:",
    "   - Reference specific sections or timestamps from the transcript to back up key claims",
    "   - Organize information into digestible chunks using headings, bullet points, or lists",
    "   - Use direct quotes from the transcript when they add value or clarity",

    "2. User Engagement:",
    "   - If the user query lacks detail, ask clarifying questions before answering",
    "   - Break down complex or multi-part queries to ensure complete, structured responses",
    "   - Offer follow-up insights or related topics based on the conversation and transcript context",

    "3. Transparency and Limits:",
    "   - Clearly communicate when information is missing or unavailable in the transcript",
    "   - Offer reasonable alternatives or directions when the original question cannot be fully answered",
    "   - Be upfront about the limitations of the transcript or ambiguity in the content"
"""
)

# Create and use the agent
rag_agent = Agent(
    name="Rag Agent",
    role="Search information from collections",
    model=OpenAIChat(id=settings.LLM_MODEL_NAME, api_key=settings.OPENAI_API_KEY),
    knowledge=knowledge_base,
    show_tool_calls=True,
    enable_session_summaries=True,
    add_references=True,
    search_knowledge=True,  # This setting gives the model a tool to search the knowledge base for information
    markdown=True,  # This setting tellss the model to format messages in markdown
    debug_mode=True,
    description=description,
    instructions=instructions,
)
