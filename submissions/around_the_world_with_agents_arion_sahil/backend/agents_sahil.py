from textwrap import dedent
import json
from typing import Dict, List

from agno.agent import Agent
from agno.team.team import Team
#from agno.models.groq import Groq
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.reasoning import ReasoningTools
from pydantic import BaseModel, Field

import os 
from dotenv import load_dotenv
load_dotenv()
#GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# ------------------------
# Schemas
# ------------------------
class TransportInfo(BaseModel):
    route: str
    price: str
    time: str
    distance: str

class LocationSpots(BaseModel):
    spots: List[str]

class SightseeingInfo(BaseModel):
    description: str

class HotelInfo(BaseModel):
    name: str
    price: str
    distance: str

# ------------------------
# Agents
# ------------------------
transport_agent = Agent(
    name="Transport Agent",
    role="Get transport route, cost, time, and distance between locations.",
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[DuckDuckGoTools()],
    instructions=[
        "Use 'duckduckgo_search' for transport info between 'from_location' and 'to_location'.",
        "Extract 'route', 'price', 'time', and 'distance'.",
        "Return JSON as per TransportInfo."
    ],
    markdown=True,
)

location_agent = Agent(
    name="Location Agent",
    role="List top 2 locations around the country for a destination.",
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[DuckDuckGoTools()],
    instructions=[
        "Use 'duckduckgo_search' to find popular tourist attractions in 'destination'.",
        "Return JSON with 'spots' list."
    ],
    markdown=True,
)

sightseeing_agent = Agent(
    name="Sightseeing Agent",
    role="Provide 2 sightseeing highlights for a location.",
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[DuckDuckGoTools()],
    instructions=[
        "Use 'duckduckgo_search' for sightseeing tips in 'location'.",
        "Return JSON as per SightseeingInfo."
    ],
    markdown=True,
)

hotel_booking_agent = Agent(
    name="Hotel Booking Agent",
    role="Recommend 2 hotels in a location under budget.",
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[DuckDuckGoTools()],
    instructions=[
        "Use 'duckduckgo_search' to find hotels in 'location' under 'budget'.",
        "Extract 'name', 'price', and 'distance'. Return JSON per HotelInfo."
    ],
    markdown=True,
)

# ------------------------
# Team Leader
# ------------------------
team_leader = Team(
    name="Team Leader Agent",
    mode="coordinate",
    model=OpenAIChat(id="gpt-4o-mini"),
    members=[transport_agent, location_agent, sightseeing_agent, hotel_booking_agent],
    tools=[ReasoningTools(add_instructions=True)],
    instructions=[
        "1. Call Transport Agent with {'from_location': from, 'to_location': to} to get start-to-destination transport.",
        "2. Call Location Agent with {'destination': to} to get tourist locations.",
        "3. From arrival airport to first tourist location: call Transport Agent.",
        "4. For each spot:",
        "   a. Call Sightseeing Agent with {'location': spot}.",
        "   b. Call Hotel Booking Agent with {'location': spot, 'budget': budget}.",
        "   c. If not first spot, call Transport Agent with {'from_location': previous_spot, 'to_location': spot}.",
        "5. From last tourist location to departure airport: call Transport Agent.",
        "6. Finally, call Transport Agent with {'from_location': to, 'to_location': from} to get return trip.",
        "7. Merge all into a comprehensive JSON travel plan including inter-location transport."
    ],
    markdown=True,
    show_members_responses=True,
    enable_agentic_context=True,
    success_criteria="Complete round-trip travel plan with attractions, inter-location transport, hotels, and sightseeing."
)

# ------------------------
# Main Execution
# ------------------------
def main(start_location: str, end_location: str, days: int, budget: str):
    task_dict = {
        "from": start_location,
        "to": end_location,
        "budget": budget,
        "days": days
    }

    # Convert dict to string for Agno compatibility
    task = {
        "role": "user",
        "content": json.dumps(task_dict)
    }

    response = team_leader.run(task)

    plan_data = 0
    if hasattr(response, "content"):
        plan_data = response.content
    elif hasattr(response, "result"):
        plan_data = response.result
    else:
        plan_data = response
    
    return plan_data
    


if __name__ == "__main__":
    plan_data = main(start_location="Delhi", end_location="Japan", days=5, budget="$10000")
    if isinstance(plan_data, dict):
        print(json.dumps(plan_data, indent=2))
    else:
        print(plan_data)