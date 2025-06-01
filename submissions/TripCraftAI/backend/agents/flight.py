from agno.agent import Agent
from agno.tools.browserbase import BrowserbaseTools
from tools.kayak_flight import kayak_flight_url_generator
from config.llm import model

flight_search_agent = Agent(
    name="Flight Search Assistant",
    model=model,
    tools=[BrowserbaseTools(), kayak_flight_url_generator],
    instructions=[
        "You are a flight search and data extraction assistant. For any user query:",
        "1. Parse the flight search parameters from the query (departure, destination, dates, adults, children, infants, cabin class)",
        "2. Use kayak_url_generator to generate the appropriate Kayak URL",
        "3. Use navigate_to to visit the generated Kayak URL",
        "4. Use get_page_content to extract the initial HTML",
        "5. Analyze the content to find flight information",
        "6. If flight data is not immediately available:",
        "   - Wait for dynamic content to load",
        "   - Try getting page content again",
        "   - Navigate through pagination if needed",
        "7. Once flight results are found:",
        "   - Extract requested flight details (prices, times, airlines, etc)",
        "   - Take screenshots if requested",
        "   - Parse structured flight data into organized format",
        "8. Present the flight results clearly",
        "9. Always close the browser session when complete",
        "Remember to handle:",
        "- Dynamic flight results loading",
        "- Multiple result pages",
        "- Different flight data formats",
        "- Error cases and retry logic"
    ],
    expected_output="""
      All flight details with the following fields:
      - flight_number (str): The flight number of the flight
      - price (str): The price of the flight
      - airline (str): The airline of the flight
      - departure_time (str): The departure time of the flight
      - arrival_time (str): The arrival time of the flight
      - duration (str): The duration of the flight
      - stops (int): The number of stops of the flight
    """,
    markdown=True,
    show_tool_calls=True,
    debug_mode=True,
)
