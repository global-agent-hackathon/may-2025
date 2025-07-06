from agno.models.openai import OpenAIChat
from agno.team.team import Team
from agents.trello_agent import trello_agent
from agents.rag_agent import rag_agent
from config import settings
from textwrap import dedent
from agno.tools.reasoning import ReasoningTools

instructions = dedent(
    """\
You are a team of AI assistants that handle meeting-related queries and Trello task updates.

Responsibilities:
1. If the user asks a question about meetings, use the **rag_agent** to search the vector store database and provide a helpful answer.
2. If the user wants to update a Trello task, use the **trello_agent** to make the appropriate changes to the Trello card.

Guidelines:
• Always use the "ai-agent" Trello board.
• Unless specified otherwise, add new tasks to the **To-Do** list (available lists: To-Do, In Progress, Review, Done).
• If you encounter an issue, explain it clearly and suggest a solution.
"""
)


team_agents_slack = Team(
    name="Online Workflow Executor",
    mode="coordinate",
    model=OpenAIChat("gpt-4.1", api_key=settings.OPENAI_API_KEY),
    members=[rag_agent, trello_agent],
    tools=[ReasoningTools(add_instructions=True)],
    show_tool_calls=True,
    markdown=True,
    debug_mode=True,
    show_members_responses=True,
    share_member_interactions=True,
    instructions=instructions,
    success_criteria="The team has successfully completed **all** the tasks. Do not stop until completing all tasks.",
)
