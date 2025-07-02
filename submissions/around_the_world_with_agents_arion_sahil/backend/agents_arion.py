import asyncio
import os
from textwrap import dedent
from dotenv import load_dotenv
from agno.agent import Agent, RunResponse
from agno.models.groq import Groq
# from agno.models.openai import OpenAIChat
from agno.team.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.reasoning import ReasoningTools
from agno.tools.mcp import MCPTools, MultiMCPTools
# from agno.tools.yfinance import YFinanceTools

# from config import CONFIG

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

## Transport Agent
transport_agent = Agent(
    name = "Transport Agent",
    role = "Fetches transportation information from a given location to another location.",
    model = Groq(id = "llama-3.3-70b-versatile"),
    tools = [DuckDuckGoTools(fixed_max_results=2)],
    instructions = ["Come up with a plan to get from one location to another. Use the tools provided to find the best route.", "Add the sources", "Add the prices", "Add the time taken", "Add the distance", "Add the transportation options", "Add the best route"],
    markdown = True,
)

## Team Leader Agent
team_leader = Team(
    name = "Team Leader Agent",
    mode = "coordinate",
    model = Groq(id = "llama-3.3-70b-versatile"),
    members = [transport_agent],
    tools = [ReasoningTools(add_instructions=True), DuckDuckGoTools()],
    instructions = [
        "Use the tools provided to reason about the problem and come up with a plan.",
        "Coordinate with the other agents to ensure that they are all working towards the same goal.",
        "Use the tools provided to find the best route.",
        "Use the tools provided to find the best transportation options.",
    ],
    markdown = True,
    show_members_responses = True,
    enable_agentic_context = True,
    success_criteria = "The team has successfully completed the task.",
)


async def google_maps(query: str) -> str:
    """ Fetches the Google Maps response for a given query. """
    
    async with MultiMCPTools(
        [
            # "npx -y @openbnb/mcp-server-airbnb --ignore-robots-txt",
            "npx -y @modelcontextprotocol/server-google-maps",
        ],
        env = {"GOOGLE_MAPS_API_KEY": GOOGLE_MAPS_API_KEY},
    ) as mcp_tools:
        agent = Agent(
            tools = [mcp_tools],
            markdown = True,
            show_tool_calls = True,
        )
        
        await agent.aprint_response(query)


def main(start_location: str, end_location: str):
    
    task = f"""
    You are a team of agents that need to get from {start_location} to {end_location}.
    You need to come up with a detailed plan that includes the cheapest route, transportation options, and any other relevant information.
    You will be using the tools provided to find the best route and transportation options.
    You will also be using the tools provided to reason about the problem and come up with a plan.
    You will be using the tools provided to coordinate with the other agents to ensure that they are all working towards the same goal.
    """
    
    team_leader.print_response(
        task,
        stream = True,
        stream_intermediate_steps = True,
        show_full_reasoning = True,
    )
    

if __name__ == "__main__":
    start_location = "Ranchi"
    end_location = "Gangtok"
    main(start_location, end_location)
    
    # asyncio.run(
    #     google_maps("What are some cheap options to stay in Kolkata for 6 people for 3 days and 2 nights?"),
    # )