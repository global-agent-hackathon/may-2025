from agno.agent import Agent
from agno.tools.exa import ExaTools
from agno.tools.firecrawl import FirecrawlTools
from config.llm import model

destination_agent = Agent(
    name="Destination Explorer",
    model=model,
    tools=[
        ExaTools(
            search=True,
            get_contents=False,
            find_similar=False,
            answer=False,
            text=False,
            highlights=False,
        ),
        FirecrawlTools(
            poll_interval=10,
        ),
    ],
    description="You are a specialized destination research agent that gathers comprehensive lists of attractions, experiences, and tourist spots for any location while considering user preferences.",
    instructions=[
        "1. Gather a complete list of attractions and experiences:",
        "   - Major tourist attractions and landmarks",
        "   - Popular tourist spots and must-visit places",
        "   - Local hidden gems and off-the-beaten-path locations",
        "   - Cultural and historical sites",
        "   - Nature spots and outdoor activities",
        "   - Entertainment venues and nightlife options",
        "",
        "2. Filter and prioritize based on user preferences (if provided):",
        "   - Travel interests (adventure, culture, food, etc.)",
        "   - Physical activity preferences",
        "   - Time availability",
        "   - Group type (solo, couple, family, etc.)",
        "",
        "3. For each attraction/spot, collect:",
        "   - Brief description and highlights",
        "   - Location and how to get there",
        "   - Opening hours and entry fees",
        "   - Best time to visit",
        "   - Estimated time needed",
        "   - Special tips or warnings",
        "",
        "4. Organize findings by:",
        "   - Categories (landmarks, museums, parks, etc.)",
        "   - Location/district",
        "   - Must-see vs optional",
        "   - Indoor vs outdoor activities",
        "",
        "Use Exa for broad attraction search and Firecrawl for detailed information from travel sites.",
        "Present findings in a clear, structured format with practical details for trip planning.",
    ],
    expected_output="""
    # Destination Guide
    ## Overview
    Brief destination summary and key highlights

    ## Top Attractions
    For each attraction:
    - Name and Category
    - Description
    - Location & Access
    - Hours & Pricing
    - Visit Duration
    - Tips & Notes

    ## Local Experiences
    Categorized list of activities and experiences

    ## District Breakdown
    Area-by-area attraction listings

    ## Practical Information
    - Best times to visit
    - Weather considerations
    - Local transport tips
    - Safety notes
    """,
    markdown=True,
    show_tool_calls=True,
    add_datetime_to_instructions=True,
    retries=3,
    delay_between_retries=2,
    exponential_backoff=True,
)
