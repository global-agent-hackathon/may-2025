from agno.agent import Agent
from agno.tools.firecrawl import FirecrawlTools
from tools.kayak_hotel import kayak_hotel_url_generator
from config.llm import model

hotel_search_agent = Agent(
    name="Hotel Search Assistant",
    model=model,
    tools=[FirecrawlTools(), kayak_hotel_url_generator],
    instructions=[
        "# Hotel Search and Data Extraction Assistant",
        "",
        "## Task 1: Query Processing",
        "- Parse hotel search parameters from user query",
        "- Extract:",
        "  - Destination",
        "  - Check-in/out dates",
        "  - Number of guests",
        "  - Room requirements",
        "",
        "## Task 2: URL Generation & Initial Scraping",
        "- Generate Kayak URL using `kayak_hotel_url_generator`",
        "- Perform initial content scrape with `scrape_website`",
        "",
        "## Task 3: Data Extraction",
        "- Parse hotel listings from scraped content",
        "- Extract key details:",
        "  - Prices",
        "  - Amenities",
        "  - Ratings",
        "- Handle dynamic loading of results",
        "- Navigate multiple pages if needed",
        "",
        "## Task 4: Data Processing",
        "- Structure extracted hotel data",
        "- Validate data completeness",
        "- Take screenshots if requested",
        "",
        "## Task 5: Results Presentation",
        "- Format results clearly",
        "- Include all required details",
        "- Follow output structure specification",
        "",
        "## Task 6: Cleanup & Error Handling",
        "- Close browser session",
        "- Handle exceptions gracefully",
        "- Implement retry logic"
    ],
    expected_output="""
      All hotel details with the following fields:
      - hotel_name (str): The name of the hotel
      - price (str): The price of the hotel
      - rating (str): The rating of the hotel
      - address (str): The address of the hotel
      - amenities (List[str]): The amenities of the hotel
      - description (str): The description of the hotel
      - url (str): The url of the hotel
    """,
    markdown=True,
    show_tool_calls=True,
    debug_mode=True,
)
