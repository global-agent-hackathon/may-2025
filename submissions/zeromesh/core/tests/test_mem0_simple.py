"""
Simple test script for verifying Mem0 API key
"""

import os
import logging
from mem0 import MemoryClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_mem0_connection():
    """Test basic Mem0 connection"""
    # Get API key
    api_key = os.getenv("MEM0_API_KEY")
    if not api_key:
        logger.error("MEM0_API_KEY environment variable not set")
        return False

    try:
        # Create client
        client = MemoryClient(api_key=api_key)
        
        # Test adding a simple memory
        messages = [
            {"role": "user", "content": "Test message from ZeroMesh"}
        ]
        
        logger.info("Attempting to add test memory...")
        response = client.add(messages, user_id="test-user")
        logger.info(f"Memory added successfully: {response}")

        # Test retrieving memories
        logger.info("Attempting to retrieve memories...")
        memories = client.get_all(user_id="test-user")
        logger.info(f"Retrieved {len(memories)} memories")
        
        return True

    except Exception as e:
        logger.error(f"Error testing Mem0 connection: {e}")
        return False

if __name__ == "__main__":
    test_mem0_connection() 