Project Title
OPENJOURNEY – The AI-Powered Social Journal for Builders

Overview
OPENJOURNEY is an AI-driven social journaling platform where makers share daily progress, connect with similar builders, and discover startup journeys transparently. Think: Notion + LinkedIn + X, powered by AI.

Goal
To demonstrate how an AI agent can create daily engagement, organize open startup journeys, and recommend related builders/projects based on semantic search.

How It Works
	•	🧠 User logs in
	•	📓 Journals daily activity or project update via chat
	•	🛠️ Agent auto-generates project/journey structure
	•	🔍 Uses PgVector+Gemini to find similar builders
	•	🧑‍🤝‍🧑 Displays them as discoverable profiles

User Flow
	1.	User lands on app and chats with AI.
	2.	Agent remembers previous logs, proposes project updates.
	3.	Agent logs entries or creates projects/journeys behind the scenes.
	4.	User can view their progress, other profiles, and similar journeys.

Core Functionality
	•	Daily journaling
	•	Project creation & tracking
	•	Journey storytelling
	•	Semantic profile discovery (via PgVector)
	•	Exa-powered people & news search

Multimodal?
Currently text-only. (Optional: Later can add image upload to illustrate projects.)

Tools Used
	•	Agno Agent Framework
	•	Gemini Flash 2.5
	•	Supabase (DB, auth)
	•	PgVector
	•	Exa API
	•	FastAPI
	•	Vercel (frontend)

UI Approach
Minimalist chat UI powered by React. AI-first experience. Agent response drives user engagement instead of traditional feeds.



SETUP :

Setup Instructions

To run the OPENJOURNEY agent locally or deploy it to a cloud provider, follow these steps:

⸻

1. Environment Variables

Create a .env file in the root directory with the following content:

SUPABASE_DB_URL=postgresql+psycopg2://your_user:your_password@your_host:port/your_db
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SUPABASE_URL=https://your-project-id.supabase.co

GOOGLE_API_KEY=your_gemini_api_key
EXA_API_KEY=your_exa_api_key

2. Supabase Setup

You’ll need a running Supabase project with the following tables:
	•	projects
	•	journeys
	•	profiles
	•	daily_entries
	•	user_memories (used by Agno’s PostgresMemoryDb)
	•	agent_sessions (used by PostgresStorage for chat history)

You can auto-generate schema by syncing with your local model or use Supabase SQL editor.

Note: The agent automatically creates missing tables (like agent_sessions or user_memories) on first run if auto_upgrade_schema=True.

⸻

3. Agentic Memory

We use:
	•	PostgresMemoryDb → stores persistent user memories
	•	PostgresStorage → stores session history and summaries
	•	enable_user_memories=True + enable_session_summaries=True to retain context between chats

You don’t need Redis or external memory management — it’s fully backed by Supabase Postgres.

4. Running Locally
uvicorn openjourney_agent.authenticated_agent:app --reload

5. Frontend Integration

Make POST requests to the /chat endpoint with the following payload:

{
  "message": "Hi, I want to start a project"
}

Authorization should include the Supabase auth token in the Authorization: Bearer <token> header.
