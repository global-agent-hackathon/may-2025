from dotenv import load_dotenv
import os
from os import getenv

load_dotenv()

from textwrap import dedent
from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.team.team import Team
from agno.tools.exa import ExaTools
from agno.tools.firecrawl import FirecrawlTools
from agno.tools.reasoning import ReasoningTools

model = OpenRouter(id="google/gemini-2.0-flash-001", api_key=getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1", temperature=0.1)


def plan_travel(travel_request: str):
    """
    Main function to handle any type of travel planning request
    """
    print("🌍 Starting Comprehensive Travel Planning Process...")
    print("=" * 60)

    # Destination Research Agent - Handles delegated attraction research tasks
    destination_agent = Agent(
        name="Destination Explorer",
        role="Research destinations, attractions, and experiences when asked by team leader",
        model=model,
        tools=[ExaTools(), FirecrawlTools()],
        description="You research destinations, attractions, activities, and experiences for any type of traveler when assigned by the team leader.",
        instructions="Research destination highlights, attractions, weather, cultural experiences, accessibility, costs, and local tips. Adapt to specific travel style.",
        markdown=True,
        show_tool_calls=True,
    )

    # Accommodation Specialist - Handles delegated hotel research tasks
    accommodation_agent = Agent(
        name="Stay Finder",
        role="Research accommodations when asked by team leader",
        model=model,
        tools=[ExaTools(), FirecrawlTools()],
        description="You research hotels, hostels, vacation rentals, and all types of accommodations when assigned by the team leader.",
        instructions="Find accommodations matching budget/style. Include amenities, location, reviews, pricing, and booking info.",
        markdown=True,
        show_tool_calls=True,
    )

    # Dining Specialist - Handles delegated restaurant research tasks
    dining_agent = Agent(
        name="Culinary Guide",
        role="Research dining and food experiences when asked by team leader",
        model=model,
        tools=[ExaTools(), FirecrawlTools()],
        description="You research restaurants, food markets, culinary experiences, and dining options when assigned by the team leader.",
        instructions="Research restaurants, local cuisine, food markets, culinary experiences. Include dietary restrictions, prices, and operating hours.",
        markdown=True,
        show_tool_calls=True,
    )

    # Transportation Specialist - Handles delegated transport research tasks
    transport_agent = Agent(
        name="Route Planner",
        role="Research transportation and logistics when asked by team leader",
        model=model,
        tools=[ExaTools(), FirecrawlTools()],
        description="You research all transportation options and travel logistics when assigned by the team leader.",
        instructions="Research flights, local transport, car rentals, public transit. Include costs, routes, travel times, and booking tips.",
        markdown=True,
        show_tool_calls=True,
    )

    # Budget Specialist - Handles delegated cost research tasks
    budget_agent = Agent(
        name="Budget Optimizer",
        role="Calculate costs and optimize travel budgets when asked by team leader",
        model=model,
        tools=[ExaTools(), FirecrawlTools()],
        description="You research costs, compare prices, and optimize travel budgets when assigned by the team leader.",
        instructions="Research pricing, compare options, find deals, create budget breakdowns. Include hidden costs and money-saving strategies.",
        markdown=True,
        show_tool_calls=True,
    )

    # Team Leader - The ONLY agent that receives full travel requests
    travel_planning_team = Team(
        name="Comprehensive Travel Planning Team",
        mode="coordinate",
        model=model,
        members=[destination_agent, accommodation_agent, dining_agent, transport_agent, budget_agent],
        description="You are the master coordinator who receives complete travel requests and creates comprehensive travel plans for any type of traveler or trip.",
        instructions=dedent("""\
            Analyze travel requests and delegate to specialists:
            - Destination Explorer: attractions/experiences
            - Stay Finder: accommodations
            - Culinary Guide: dining/food
            - Route Planner: transportation
            - Budget Optimizer: costs/optimization

            Create complete plans with accommodation, daily itinerary, dining, transport, budget, and practical tips.
            Adapt to travel style (business, adventure, luxury, budget, solo, group)."""),
        expected_output=dedent("""\
            # Travel Itinerary
            ## Trip Overview
            ## Accommodations 🏨
            ## Daily Itinerary
            ## Dining 🍽️
            ## Transportation 🚊
            ## Budget 💰
            ## Tips & Contacts 📝
            """),
        markdown=True,
        show_members_responses=True,
        enable_agentic_context=True,
        add_datetime_to_instructions=True,
        debug_mode=True
    )

    # Generate the travel plan
    response = travel_planning_team.print_response(
        travel_request,
        stream=True,
        stream_intermediate_steps=True,
        show_full_reasoning=True,
    )

    return response

# Example usage - can handle any type of travel
if __name__ == "__main__":
    # Sample travel request - adaptable to any travel style
    sample_request = """
    Please create a comprehensive travel plan with the following requirements:

    Travelers: 2 adults, 1 child (age 6), stroller-friendly
    Destination: Singapore
    Dates: Any 5 days in late June
    Budget: ₹2.2L total (~₹73K/person)
    Style: Family-friendly, cultural + relaxing
    Stay: 3–4 star hotel, pool, near MRT, breakfast included
    Activities: Universal Studios, aquarium, zoo, shopping, Indian food
    Transport: Flights – Economy; local – MRT/bus
    Diet: Pure vegetarian (no onion/egg)
    Pacing: Moderate (1–2 spots/day)
    Past Trips: Dubai 2023 – liked metro access, disliked too much sun walking

    Please provide a detailed itinerary with day-by-day plans, accommodation recommendations,
    dining options for dietary requirements, transportation details, and a complete budget breakdown.
    """

    plan_travel(sample_request)