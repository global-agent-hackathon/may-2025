from agno.models.google import Gemini
from agents.agentsUtility import *
from agno.team.team import Team
from agno.memory.v2.memory import Memory
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.storage.sqlite import SqliteStorage
from utilities.getResourcePath import get_asset_path


class MainAgent:
    def __init__(self, apiKey: str, model: str):
        self.apiKey = apiKey
        self.model = model
        self.memory_db = SqliteMemoryDb(
            table_name="team_memory", db_file=get_asset_path("memory.db"))
        self.memory = Memory(db=self.memory_db)
        self.storage = SqliteStorage(
            table_name="team_session", db_file=get_asset_path("memory.db"))
        self.userId = "user"
        self.sessionId = "session"

    async def initiateMainAgent(self, prompt: str) -> str:
        router_agent = Team(
            name="Route agent",
            model=Gemini(api_key=self.apiKey, id=self.model),
            mode="route",
            memory=self.memory,
            enable_agentic_memory=True,
            enable_user_memories=True,
            enable_agentic_context=True,
            markdown=True,
            enable_team_history=True,
            num_of_interactions_from_history=5,
            members=[AgentsUtility.generalPurposeAgent(
                self.model, self.apiKey), AgentsUtility.terminalAgent(self.model, self.apiKey, memory=self.memory), AgentsUtility.fileSummarizeAgent(self.model, self.apiKey)],

        )
        res = await router_agent.arun(prompt, session_id=self.sessionId, user_id=self.userId)
        return str(res.content)
