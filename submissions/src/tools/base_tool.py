import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

from ..models import CryptoNewsResponse

logger = logging.getLogger(__name__)

class BaseTool(ABC):
    name: str
    description: str
    
    def __init__(self):
        if not hasattr(self, 'name') or not hasattr(self, 'description'):
            raise ValueError("Tool must have 'name' and 'description' attributes")
    
    @abstractmethod
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with the given parameters"""
        pass
    
    @abstractmethod
    def format_response(self, query: str, tool_response: Dict[str, Any]) -> CryptoNewsResponse:
        """Format the tool response into a standardized API response"""
        pass
    
    def get_metadata(self) -> Dict[str, str]:
        """Returns the tool metadata for tool selection prompting"""
        return {
            "name": self.name,
            "description": self.description
        }
        
    def create_base_response(self, query: str) -> Dict[str, Any]:
        """Create a base response structure with default values"""
        return {
            "query": query,
            "answer": "",
            "sentiment": "Neutral",
            "context": "",
            "trending_topics": ["Bitcoin", "Ethereum", "Cryptocurrency"],
            "articles": [],
            "article_analysis": None,
            "processed_at": datetime.now().isoformat()
        }