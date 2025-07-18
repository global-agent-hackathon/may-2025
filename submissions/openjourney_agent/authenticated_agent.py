from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from agno.agent import Agent, AgentKnowledge
from openjourney_agent.tools.toolkit import OpenJourneyToolkit
from openjourney_agent.supabase_client import get_user_by_token, get_user_stats, get_user_recent_entries, get_user_projects, get_profile_by_user_id
import os
from pydantic import BaseModel
from agno.models.google import Gemini
from fastapi.middleware.cors import CORSMiddleware
from agno.vectordb.pgvector import PgVector, SearchType
from openjourney_agent.vector.custom_pgvector import CustomPgVector
from agno.embedder.google import GeminiEmbedder
from dotenv import load_dotenv
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.storage.sqlite import SqliteStorage
from openjourney_agent.tools.profile_tools import display_profiles
from typing import Optional
from .supabase_client import get_user_by_token, get_user_by_id , supabase
from openjourney_agent.memory.supabase_memory import SupabaseMemoryDb, SupabaseSessionStorage
from agno.storage.postgres import PostgresStorage
from agno.memory.v2.db.postgres import PostgresMemoryDb

def create_memory():
    memory_db = PostgresMemoryDb(
        table_name="user_memories",
        schema="public",  
        db_url=os.getenv("SUPABASE_DB_URL")  
    )
    return Memory(
        model=Gemini(id="gemini-2.5-flash-preview-05-20"),  
        db=memory_db
    )


def create_storage():
    return PostgresStorage(
        table_name="agent_sessions",
        schema="public",  # Supabase default schema
        db_url=os.getenv("SUPABASE_DB_URL"),  # already set in your .env
        auto_upgrade_schema=True
    )

storage = PostgresStorage(
    table_name="agent_sessions",
    schema="public",  
    db_url=os.getenv("SUPABASE_DB_URL"),  
    auto_upgrade_schema=True  
)


"""# Initialize Memory
def create_memory():
    return Memory(
        db=SqliteMemoryDb(
            table_name="memory",
            db_file="tmp/memory.db",  
        ),
    )

# Initialize Storage (optional, for session summaries)
def create_storage():
    return SqliteStorage(
        table_name="agent_sessions",
        db_file="tmp/agent_sessions.db", 
    )
"""
load_dotenv()
db_url = os.getenv("SUPABASE_DB_URL")

last_found_profiles = None

gemini_api_key = os.getenv("GOOGLE_API_KEY")

gemini_embedder = GeminiEmbedder(dimensions=768)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


'''
vector_db = CustomPgVector(
    table_name="new_journey_search_view",
    schema="public",
    db_url=db_url,
    search_type=SearchType.hybrid,
    embedder=GeminiEmbedder(dimensions=768),
)
'''
vector_db = PgVector(
    table_name="new_journey_search_view",
    schema="public",
    db_url=db_url,
    search_type=SearchType.hybrid,
    embedder=GeminiEmbedder(dimensions=768),
)

knowledge_base = AgentKnowledge(
    vector_db=vector_db,
    content_column=["id", "title", "description", "embedding"], 
    metadata_column=[
    "id", "title", "user_id", "username",
    "profile_name", "bio", "location", "profile_pic"
]
)

#knowledge_base.load(upsert=True)

# 1. Auth: Get current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = await get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user

# 2. User context
async def get_user_context(user_id):
    user = await get_user_by_id(user_id)

    if not user:
        raise Exception("❌ Failed to resolve user from ID or user not found")

    stats = await get_user_stats(user["id"])
    projects = await get_user_projects(user["id"], limit=3)
    recent = await get_user_recent_entries(user["id"], limit=3)
    project_map = {p["title"]: p["id"] for p in projects}

    return {
        "name": user["full_name"] or user["username"],
        "streak": stats.get("streak_days", 0),
        "projects": [p["title"] for p in projects],
        "project_map": project_map,
        "entries": [e["message"] for e in recent],
    }


def profile_retriever(agent: Agent, query: str, num_documents: Optional[int], **kwargs) -> Optional[list[dict]]:
        # Embed the query
        query_embedding = knowledge_base.embed(query)

        # Query journey_search_view for top matches
        results = knowledge_base.search(query_embedding, top_k=num_documents)

        # Group by user_id
        profiles = {}
        for doc in results:
            uid = doc["metadata"]["user_id"]
            if uid not in profiles:
                profiles[uid] = {
                    "name": doc["metadata"].get("profile_name"),
                    "bio": doc["metadata"].get("profile_bio"),
                    "location": doc["metadata"].get("location"),
                    "projects": []
                }
            profiles[uid]["projects"].append({
                "title": doc["metadata"].get("project_title"),
                "tech_stack": doc["metadata"].get("tech_stack"),
                "ai_tools": doc["metadata"].get("ai_tools"),
                "mrr": doc["metadata"].get("mrr"),
                "snippet": doc["text"][:200]
            })

        return [{"text": f"Founder: {p['name']}\nBio: {p['bio']}\nProjects: {len(p['projects'])}", "metadata": p} for p in profiles.values()]


# 3. Create user-scoped agent
def create_agent_for_user(user_id, user_context):
    toolkit = OpenJourneyToolkit(user_id=user_id, knowledge=knowledge_base)
    memory = create_memory()
    storage = create_storage()
    latest_project = user_context["projects"][0] if user_context["projects"] else None
    return Agent(
    name="Journal Friend",
    agent_id="journal-friend",
    add_history_to_messages=True,
    num_history_responses=50,
    model=Gemini(id="gemini-2.5-flash-preview-05-20"),
    tools=[toolkit],
    context={
            "user_name": user_context["name"],
            "current_project": latest_project if latest_project else "None",
           #"streak_days": user_context["streak"],
            "recent_entries": "\n".join(user_context["entries"]) if user_context["entries"] else "No recent entries."
        },
    description= """
You are Orbit, a warm and curious AI journaling friend for {name}.

{name} is currently working on: {project}.
They’ve journaled about: {entries}.
""".format(
    name=user_context["name"],
    project=latest_project or "a new idea",
    entries=", ".join(user_context["entries"]) if user_context["entries"] else "nothing yet"
),
    instructions=[
                            """
1. Daily Journaling ✍️
                    - Ask how their day is going or what they’re working on
                    - Reflect on their mood or goals empathetically
                    - Log their entry with `log_entry`, optionally tagging mood, do not use it for journey creation, log entry is something you do behind without users knowledge

                    2. Project Support 🛠️
                    - If a user shares a project idea or title, help them clarify it
                    - Immediately call `create_project` once you have enough detail
                    - Don’t drop the topic until the project is created

                    3. Journey Storytelling 📚
                    - After project creation, use `create_journey` to document their ongoing progress
                    - Make stroytelling for their project, because other people also will be interested.
                    - Encourage transparency around tools, revenue, challenges

                    4. Vibes & Human Feel 🌱
                    - Use emojis sparingly for warmth 😊
                    - Be a motivating presence, not a productivity bot
                    - Remind users to enjoy the ride

                

5. Profile Display 🎯
- When you retrieve people or profiles using any tool (e.g. `search_knowledge_base`, `find_related_journeys_and_people`), always pass their metadata (bio, location, username, etc.) to `display_profiles_from_results`.
- Do **not** mention user IDs directly in the conversation.
- Let the markdown output from `display_profiles_from_results` speak for itself — do not summarize or repeat profile details afterward.
- Always include the tool's output as part of your response (this requires `return_tool_outputs=True` in the agent config).
- Always display the profiles with links, like in the tool output.
6. Project Overview 🗂️
- When a user asks “What are my projects?”, “Show all projects”, or anything similar, call the `show_all_projects` tool.
- Use card-style formatting to present each project clearly: include title, tech stack, MRR/ARR, status, and last progress if available.
- If the user asks for the latest project or “what was I working on?”, use `resume_latest_project`.

 7. Discovery & Research 🌍
- You can find interesting startup founders based on field or location using Exa-powered tools.
- If the user mentions a specific technology (e.g. AI, blockchain), search for similar builders or projects.
- Retrieve personal websites or LinkedIn profiles when the user gives you a name and (optionally) a school or context.
- Fetch recent news from sites like TechCrunch, Hacker News, Product Hunt, and Indie Hackers if the user wants updates.
- Use comparisons to help users understand differences between startups, tools, or tech stacks (e.g., "Compare Linear vs Height").

Use these tools to help the user explore the ecosystem and connect meaningfully. Do not just give generic web results — use the search tools when specific queries arise.

Note: You’re a friend for the long ride, not just a one-time check-in. Celebrate consistency, progress, and honest storytelling. AND DO NOT MENTION TOOLS YOU HAVE JUST MENTION WHAT YOU CAN DO, DONT USE TOOLS NAMES
"""
    ],
    markdown=True,
    show_tool_calls=True,
    knowledge=knowledge_base,
    search_knowledge=True,
    #retriever=profile_retriever,
    memory=memory,
    enable_user_memories=True,
    enable_session_summaries=True,  
    storage=storage,
    session_id=user_id,
    read_chat_history=True,
    debug_mode=True
)

# 4. Main chat endpoint
class ChatRequest(BaseModel):
    message: str

def clean_messages(messages):
    return [
        m for m in messages
        if hasattr(m, "content") and isinstance(m.content, str) and m.content.strip()
    ]

def safe_run(agent, message, user_context=None, instructions=None):
    user_context = user_context or {}
    instructions = instructions or []

    # Combine message + personalization
    run_result = agent.run(
        message,
        user_context=user_context,
        instructions=instructions,
        return_messages=True  # This gives access to all internal messages
    )

    # Extract and sanitize messages before sending to model
    raw_messages = run_result.messages
    clean_messages = [m for m in raw_messages if m.get("content") and m["content"].strip()]

    # Manually call model with clean messages
    response = agent.model.response(messages=clean_messages)
    return response

@app.post("/chat")
async def chat_endpoint(request: ChatRequest, user=Depends(get_current_user)):
    message = request.message

    if not message or not message.strip():
        return {"response": "❌ Please provide a valid message."}

    user_id = user["id"]
    user_context = await get_user_context(user_id)

    personalization = f"""
    You are speaking to {user_context['name']}. 
    They have a {user_context['streak']} day streak.
    Their projects include: {', '.join(user_context['projects'])}.
    Recent journal highlights: {', '.join(user_context['entries'])}.
    """

    agent = create_agent_for_user(user_id, user_context)

    full_context = {
    "user_id": user_id,
    "user_name": user_context["name"],
    "current_project": user_context["projects"][0] if user_context["projects"] else "None",
    "recent_entries": "\n".join(user_context["entries"]) if user_context["entries"] else "No recent entries."
    }

    try:
        run_result = agent.run(
            message,
            user_context=full_context,
            instructions=[personalization],
            return_tool_outputs=True
        )

        # Separate tool output and main content
        response = {
            "tool_output": run_result.tool_output if hasattr(run_result, "tool_output") else None,
            "content": run_result.content or "",
            "full_response": ""
        }

        # Combine them for backward compatibility
        if response["tool_output"]:
            response["full_response"] = response["tool_output"] + "\n\n" + response["content"]
        else:
            response["full_response"] = response["content"]

        return response
    except Exception as e:
        print("❌ Agent Error:", e)
        return {"response": f"❌ Error: {str(e)}"}