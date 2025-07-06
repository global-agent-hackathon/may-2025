from agno.models.openai import OpenAIChat
from agno.team.team import Team
from agents.trello_agent import trello_agent
from agents.slack_agent import slack_agent
from agents.summarizer_agent import summarizer_agent
from config import settings
from textwrap import dedent
from agno.tools.reasoning import ReasoningTools

instructions = dedent(
    """\
You are a team of AI meeting assistants responsible for executing a structured workflow to summarize meetings, notify attendees, and create follow-up tasks.

Your responsibilities must be completed **step-by-step in the exact order** below.

Step 1 – Summarize the meeting using the summarizer_agent.

Step 2 – Use slack_agent to post a message in the #meetings-repository channel.

Step 3 – Use trello_agent to create a Trello card for each action item.

"""
)

team_agents = Team(
    name="Workflow Executor",
    mode="coordinate",
    model=OpenAIChat("gpt-4.1", api_key=settings.OPENAI_API_KEY),
    members=[summarizer_agent, trello_agent, slack_agent],
    tools=[ReasoningTools(add_instructions=True)],
    show_tool_calls=True,
    markdown=True,
    debug_mode=True,
    show_members_responses=True,
    share_member_interactions=True,
    instructions=instructions,
    success_criteria="The team has successfully completed **all** the tasks. Do not stop until completing all tasks.",
)
