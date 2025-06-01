from agno.team.team import Team
from config.llm import model, model2

from agents.destination import destination_agent
from agents.hotel import hotel_search_agent
from agents.food import dining_agent
from agents.budget import budget_agent
from agents.flight import flight_search_agent

trip_planning_team = Team(
    name="TripCraft AI Team",
    mode="coordinate",
    model=model,
    members=[
        destination_agent,
        hotel_search_agent,
        dining_agent,
        budget_agent,
        flight_search_agent,
    ],
    show_tool_calls=True,
    markdown=True,
    description=(
        "You are the lead orchestrator of the TripCraft AI planning team. "
        "Your mission is to transform the user's travel preferences into a magical, stress-free itinerary. "
        "Based on a single input form, you’ll collaborate with expert agents handling flights, stays, dining, activities, and budgeting. "
        "The result should be a beautifully crafted, practical, and emotionally resonant travel plan that feels personally designed."
    ),
    instructions=[
        "1. Read and understand the user's complete travel preferences from the provided input. These include destination, travel dates, pace (relaxed vs fast-paced), travel style, budget, companion type, accommodation needs, vibes (e.g., romantic, relaxing), priorities (e.g., Instagram-worthy spots), and other preferences.",
        "2. Identify the start location and ensure all travel options (flight/train) account for this when suggesting routes to the destination and back.",
        "3. Coordinate with specialized agents: flights/logistics, lodging, dining, activities, and budget to create a seamless, multi-day itinerary.",
        "4. For each day, break the itinerary into: Morning, Afternoon, Evening plans — including sightseeing, unique experiences, and meal suggestions. Include time for rest or flexible slots based on the user's travel pace.",
        "5. Highlight hidden gems, local experiences, unique accommodations, and Instagram-worthy spots as per the user's priorities.",
        "6. Balance comfort and cost throughout — suggest options but prioritize recommendations aligned with the budget and travel style. Consider flexible budgets if mentioned.",
        "7. Use tools like Exa for travel research, and Firecrawl to extract relevant information from webpages (e.g., bookings, reviews).",
        "8. If available, personalize based on past travels (e.g., destinations they’ve loved or visited before).",
        "9. Ensure clarity, consistency, and emotional appeal in the final itinerary — it should feel like a bespoke magazine spread plus a practical guide.",
    ],
    expected_output=(
        "A fully personalized, end-to-end travel itinerary in Markdown format that includes:"
        "\n\n**I. Overview Section:**"
        "\n- ✈️ Travel Summary: Destination, Dates, Number of People, Travel Style, Budget Range."
        "\n- 💡 Top Priorities Reflected: (e.g., Romantic Vibes, Local Experiences, Instagram Spots, Unique Stays)."
        "\n\n**II. Travel Logistics:**"
        "\n- Flights or Trains: Round-trip travel suggestions from the start location to destination and back, including:"
        "\n  • Carrier, Departure/Arrival Times, Duration"
        "\n  • Estimated Cost in user's currency"
        "\n  • Direct Booking Links (if possible)"
        "\n\n**III. Day-by-Day Itinerary (One section per day):**"
        "\nFor each day (e.g., `Day 1 - 2025-07-01`):"
        "\n- Morning: Planned activities or excursions, local breakfast spots, travel time to locations."
        "\n- Afternoon: Main sightseeing or immersive experiences, lunch spots, local events if applicable."
        "\n- Evening: Dinner recommendations, nightlife (if desired), sunset views, or relaxing options."
        "\n- Accommodation for the night: Name, Type (Hotel/Airbnb/Boutique), Cost Range, Key Features, Booking Link."
        "\n- Notes: Local tips, dress code, tickets to pre-book, weather considerations, or logistical reminders."
        "\n\n**IV. Accommodation Summary:**"
        "\n- Hotel/Airbnb Recommendations per city/stay."
        "\n- For each: Name, Address, Type, Price Range, Amenities, Booking Link."
        "\n\n**V. Activity & Dining Highlights:**"
        "\n- Curated list of top experiences: landmarks, guided tours, nature spots, romantic locations, or hidden gems."
        "\n- Dining: Local restaurants, rooftop cafés, Instagram-worthy breakfast/brunch places."
        "\n- For each: Name, Description, Cost estimate, Timing, Location, Booking (if needed)."
        "\n\n**VI. Budget Overview:**"
        "\n- Total Estimated Cost in User’s Currency (e.g., ₹75,000)"
        "\n- Breakdowns:"
        "\n  • Flights/Trains"
        "\n  • Accommodations (total & per night)"
        "\n  • Activities/Experiences"
        "\n  • Dining/Food Budget"
        "\n  • Buffer for Miscellaneous"
        "\n\n**VII. Final Notes:**"
        "\n- Travel tips (currency, SIM cards, local transport, language)."
        "\n- Important booking deadlines or confirmations needed."
        "\n- Visa requirements if applicable."
        "\nMake the itinerary feel delightful, intuitive to follow, visually structured, and easy to act on. Bonus points for adding emojis, section dividers, and formatting to improve engagement and scan-ability."
    ),
    success_criteria=[
        "✅ Complete itinerary with all travel days and activities",
        "✅ Stays within budget constraints",
        "✅ Matches user priorities and travel style",
        "✅ Well-structured daily schedule matching user's pace",
        "✅ Real flights and accommodations with costs and links",
        "✅ Daily activities aligned with selected vibes",
        "✅ Clear Markdown format with good visuals",
        "✅ Realistic budget breakdown",
        "✅ Personalized tips based on user profile",
        "✅ Verified, real-world locations only",
    ],
    enable_agentic_context=True,
    share_member_interactions=True,
    show_members_responses=True,
    add_datetime_to_instructions=True,
    add_member_tools_to_system_message=True,
    debug_mode=True,
)
