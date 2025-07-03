from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import DuckDuckGoSearchException
from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import os
from agno.tools import tool
from agno.agent import Agent
from agno.models.groq import Groq
load_dotenv()

@tool
def get_manim_docs(query: str, doc_length: int)-> list[str]:
    """
    Search and retrieve Manim documentation content based on a query.
    
    This function performs the following steps:
    1. Searches the web for Manim documentation pages matching the query
    2. Scrapes the content of the top results
    3. Returns the content in markdown format
    
    Args:
        query (str): The search term or question about Manim functionality
        doc_length (int): Maximum number of documentation results to return
        
    Returns:
        list: A list of markdown strings containing the scraped documentation content, or an empty list on error.
        
    """
    base_url = " site:https://docs.manim.community"
    # search_query = query + base_url
    # Instead of site: operator, try:
    search_query = f"manim {query} documentation"
    results = [] # Initialize results as an empty list
    try:
        results = DDGS().text(search_query, max_results=doc_length)
    except DuckDuckGoSearchException as e:
        print(f"DuckDuckGo search failed due to rate limit or other error: {e}")
        print(f"Query that failed: {search_query}")
        return [] # Return empty list on error
    except Exception as e: # Catch any other potential errors during the search
        print(f"An unexpected error occurred during DuckDuckGo search: {e}")
        print(f"Query that failed: {search_query}")
        return []

    doc_links = []
    if results: # Proceed only if results were successfully fetched
        for i in results:
            try:
                doc_links.append(i["href"])
            except Exception as e:
                print(f"Error extracting href from DDGS result item: {i}, error: {e}")
                continue
    else:
        print("No results from DuckDuckGo search.")
        return []

    if not doc_links:
        print("No document links extracted from search results.")
        return []

    app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

    md_doc = []
    for url in doc_links:
        scrape_result = app.scrape_url(url, formats=['markdown'])
        try:
            md_doc.append(scrape_result.markdown)
        except Exception as e:
            md_doc.append(e)


    return md_doc

def main():
    agent = Agent(
        model=Groq(id="llama-3.3-70b-versatile"),
        description="You are an animator using manin to write code for animation use manim_doc tool to search documentation",
        tools=[get_manim_docs],      
        show_tool_calls=True,           
        markdown=True                   
        )

    agent.print_response("create an animation of rotaing cube", stream=True)

if __name__ == "__main__":
    main()