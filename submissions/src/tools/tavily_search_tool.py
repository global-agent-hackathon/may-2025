import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

from .base_tool import BaseTool

logger = logging.getLogger(__name__)

try:
    from tavily import TavilyClient
except ImportError:
    raise ImportError("`tavily-python` not installed. Please install using `pip install tavily-python`")

class TavilySearchTool(BaseTool):
    name = "tavily_search"
    description = "Search for real-time web results using the Tavily API. Use this for up-to-date information from the web."

    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("TAVILY_API_KEY", "")
        if not self.api_key:
            logger.error("TAVILY_API_KEY not provided")
        self.client = TavilyClient(api_key=self.api_key)

    async def tavily_search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        logger.info(f"Searching web with Tavily: query='{query}', max_results={max_results}")
        try:
            response = self.client.search(query=query, max_results=max_results)
            return response.get("results", [])
        except Exception as e:
            logger.error(f"Tavily API error: {e}")
            return []

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query = params.get("query", "")
        max_results = params.get("limit", 5)
        logger.info(f"Executing Tavily search tool (query='{query}', max_results={max_results})")
        if not query:
            logger.warning("No query provided for Tavily search")
            return self.create_base_response("")
        results = await self.tavily_search(query, max_results)
        return {
            "query": query,
            "results": results,
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        }

    def format_response(self, query: str, tool_response: Dict[str, Any]) -> Dict[str, Any]:
        response = self.create_base_response(query)
        articles = []
        for result in tool_response.get("results", []):
            articles.append({
                "title": result.get("title"),
                "summary": result.get("content"),
                "media": None,
                "link": result.get("url"),
                "authors": [{"name": "Web Search"}],
                "published": None,
                "category": "Web Search",
                "subCategory": "Tavily",
                "language": None,
                "timeZone": None
            })
        answer = f"Found {len(articles)} relevant web results for your query." if articles else "No relevant results found."
        context = f"Based on Tavily web search for '{query}'"
        response.update({
            "answer": answer,
            "context": context,
            "articles": articles,
        })
        return response