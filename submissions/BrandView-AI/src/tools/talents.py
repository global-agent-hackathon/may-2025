from typing import Dict, Annotated
from agno.tools import tool
from agno.tools.tavily import TavilyTools
from src.tools.helper.helper import _crawl_talent_agency

@tool(
    name="crawl_talent_agency",
    description="Crawl a talent agency website to extract information about their talents/influencers.",
    show_result=True,
    cache_results=True,
    cache_ttl=3600,
    cache_dir="/tmp/agno_cache"
)
def crawl_talent_agency(
    agency_url: Annotated[str, """
        The URL of the talent agency website to crawl.
        This should be the main URL of the agency's website.
        Example: 'https://www.talentagency.com'
    """],
    limit: Annotated[int, """
        Maximum number of pages to crawl on the website.
        Default is 50. Higher values will take longer but may find more talents.
    """] = 50
) -> Dict:
    """
    Crawl a talent agency website to extract information about their talents/influencers.
    
    Args:
        agency_url (str): The URL of the talent agency website
        limit (int): Maximum number of pages to crawl (default: 50)
        
    Returns:
        Dict: A dictionary containing:
            - agency_name: Name of the talent agency
            - talents: List of talent information including:
                - name: Talent's name
                - social_links: Dictionary of social media links
                - bio: Short biography
                - categories: List of talent categories
                - stats: Dictionary of social media statistics
    """
    return _crawl_talent_agency(agency_url, limit)