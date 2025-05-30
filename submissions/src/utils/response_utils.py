import logging
import json
from typing import Dict, Any, List
from datetime import datetime
from ..constants import NEEDS_MORE_CONTEXT_PHRASES

logger = logging.getLogger(__name__)

def parse_llm_response(response_text: str) -> Dict[str, Any]:
    """Parse LLM response text to extract structured data"""
    try:
        logger.debug("Attempting to parse LLM response as JSON")
        json_content = response_text.strip()
        
        if json_content.startswith("```json"):
            logger.debug("Detected markdown JSON format, cleaning up")
            json_content = json_content.replace("```json", "", 1)
            
        if json_content.endswith("```"):
            json_content = json_content[:-3]
        
        parsed_json = json.loads(json_content.strip())
        logger.debug("Successfully parsed LLM response as JSON")
        
        if not isinstance(parsed_json, dict):
            logger.error("Parsed JSON is not a dictionary")
            return fallback_response("Response format error")
        
        return parsed_json
        
    except json.JSONDecodeError:
        logger.warning("Failed to parse LLM response as JSON, falling back to text extraction", exc_info=True)
        return extract_info_from_text(response_text)

def needs_more_context(response: Dict[str, Any]) -> bool:
    """Check if response indicates need for more context"""
    if isinstance(response, dict) and response.get("needs_more_context") is True:
        return True
    
    if isinstance(response, dict) and "answer" in response:
        text = response["answer"]
        return any(phrase in text.lower() for phrase in NEEDS_MORE_CONTEXT_PHRASES)
    
    if isinstance(response, str):
        return any(phrase in response.lower() for phrase in NEEDS_MORE_CONTEXT_PHRASES)
    
    return False

def extract_info_from_text(response_text: str) -> Dict[str, Any]:
    """Extract structured information from non-JSON response text"""
    sentiment = "Neutral"
    if "bullish" in response_text.lower():
        sentiment = "Bullish"
    elif "bearish" in response_text.lower():
        sentiment = "Bearish"
    elif "mixed" in response_text.lower():
        sentiment = "Mixed"
    
    trending_topics = ["Bitcoin", "Ethereum", "Cryptocurrency", "Market Analysis", "Trading"]
    
    return {
        "query": "Crypto market analysis",
        "answer": response_text,
        "sentiment": sentiment,
        "context": "Based on analysis of recent news.",
        "trending_topics": trending_topics,
        "article_analysis": [],
        "processed_at": datetime.now().isoformat()
    }

def fallback_response(error_message: str) -> Dict[str, Any]:
    """Generate fallback response when processing fails"""
    return {
        "query": "Crypto market analysis",
        "answer": f"I encountered an error: {error_message}. However, I can still provide you with recent cryptocurrency news.",
        "sentiment": "Neutral",
        "context": "Unable to analyze market sentiment due to an error.",
        "trending_topics": ["Bitcoin", "Ethereum", "Cryptocurrency"],
        "articles": [],
        "article_analysis": [],
        "processed_at": datetime.now().isoformat()
    }