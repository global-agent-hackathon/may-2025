from textwrap import dedent
from agno.models.openai import OpenAIChat
from agno.agent import Agent
from agno.tools.trello import TrelloTools
from config import settings


instructions = dedent(
    """\
You are a productivity assistant for managing Trello workflows.
Your role is to help users efficiently organize and track tasks on Trello.

You can assist with:
• Creating, organizing, and updating Trello boards, lists, and cards (tasks)
• Moving tasks (cards) between lists on the same board
• Retrieving information about boards, lists, and cards (tasks)

Guidelines:
• Always use the "ai-agent" board for task management.
• Add new tasks to the **To-Do** list unless another list is specified (choices: To-Do, In Progress, Review, Done).
• If an issue arises, explain it simply and suggest a solution.
"""
)


description = dedent(
    """\
A smart assistant that helps users manage their Trello boards by creating, updating, and tracking cards, lists, and boards on the "ai-agent" board.
New tasks are added to the **To-Do** list unless another list is specified.
"""
)


trello_agent = Agent(
    name="Trello Agent",
    role="Create cards in Trello",
    model=OpenAIChat(id=settings.LLM_MODEL_NAME, api_key=settings.OPENAI_API_KEY),
    instructions=instructions,
    description=description,
    tools=[
        TrelloTools(
            api_key=settings.TRELLO_API_KEY,
            api_secret=settings.TRELLO_API_SECRET,
            token=settings.TRELLO_TOKEN,
        )
    ],
    show_tool_calls=True,
)
