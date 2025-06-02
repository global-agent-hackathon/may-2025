"""
Mem0 API client for storing and retrieving memories
"""

import os
import json
import time
import logging
import httpx
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class Mem0Client:
    """Client for interacting with Mem0 API"""

    def __init__(self):
        self.api_key = os.getenv("MEM0_API_KEY")
        if not self.api_key:
            logger.warning("MEM0_API_KEY not found in environment variables")
            
        self.endpoint = "https://api.mem0.ai"
        self.collection = "zeromesh"
        self.log_buffer = []
        self.last_flush = 0
        self.fallback_mode = False

    async def initialize(self):
        """Initialize the client and test connection"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.endpoint}/v1/mem-it",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "input": "test",
                        "collection": self.collection
                    }
                )
                response.raise_for_status()
                logger.info("Successfully connected to Mem0 API")
                
        except Exception as e:
            logger.error(f"HTTP error initializing Mem0 client: {str(e)}")
            logger.warning("Falling back to local memory storage mode")
            self.fallback_mode = True

    async def store(self, collection: str, data: Dict[str, Any]):
        """Store data in Mem0"""
        if self.fallback_mode:
            # In fallback mode, store events directly
            if "events" in data:
                self.log_buffer.extend(data["events"])
            else:
                self.log_buffer.append(data)
            return

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.endpoint}/v1/mem-it",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "input": json.dumps(data),
                        "collection": collection,
                        "metadata": {"type": "audit_logs"}
                    }
                )
                response.raise_for_status()
                logger.debug(f"Successfully stored data in collection {collection}")
                
        except Exception as e:
            logger.error(f"Error storing data in Mem0: {str(e)}")
            logger.debug("Storing in local buffer")
            if "events" in data:
                self.log_buffer.extend(data["events"])
            else:
                self.log_buffer.append(data)

    async def query(self, collection: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query data from Mem0"""
        if self.fallback_mode:
            # Filter logs from local buffer
            filtered_logs = []
            for log in self.log_buffer:
                match = True
                for key, value in query.items():
                    if key == "details.agent_id":
                        if "details" not in log or log["details"].get("agent_id") != value:
                            match = False
                            break
                    elif key == "type":
                        if log.get("type") != value:
                            match = False
                            break
                    elif key not in log or log[key] != value:
                        match = False
                        break
                if match:
                    filtered_logs.append(log)
            logger.debug(f"Found {len(filtered_logs)} logs in local buffer matching query {query}")
            return filtered_logs

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.endpoint}/search",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    params={
                        "collection": collection,
                        "query": json.dumps(query)
                    }
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Error querying Mem0: {str(e)}")
            return self.log_buffer

    async def cleanup(self):
        """Clean up resources"""
        if self.log_buffer:
            logger.warning(f"Cleaning up with {len(self.log_buffer)} items in buffer")
            self.log_buffer = [] 