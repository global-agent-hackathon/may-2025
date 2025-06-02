"""
Simple example demonstrating ZeroMesh usage with OpenAI integration
"""

import asyncio
import os
from dotenv import load_dotenv
from zeromesh import ZeroMesh, ZeroMeshConfig

async def main():
    # Load environment variables
    load_dotenv()
    
    # Create configuration
    config = ZeroMeshConfig(
        mcp_host=os.getenv("MCP_HOST", "localhost"),
        mcp_port=int(os.getenv("MCP_PORT", "8000")),
        aztp_cert_path=os.getenv("AZTP_CERT_PATH", "./certs/aztp.crt"),
        aztp_key_path=os.getenv("AZTP_KEY_PATH", "./certs/aztp.key")
    )
    
    # Initialize ZeroMesh
    zeromesh = ZeroMesh(config)
    
    try:
        # Start the service
        await zeromesh.start()
        print("ZeroMesh service started")
        
        # Example: Verify a message between two agents
        sender_id = "agent1"
        recipient_id = "agent2"
        message = {
            "type": "request",
            "content": "Hello from agent1!",
            "timestamp": "2024-03-20T12:00:00Z"
        }
        
        # Verify the message
        is_allowed = await zeromesh.verify_message(sender_id, recipient_id, message)
        print(f"Message allowed: {is_allowed}")
        
        # Example: Update trust score based on interaction
        await zeromesh.update_trust_score(
            agent_id=sender_id,
            interaction_result=True,
            context={"message_type": "request", "status": "success"}
        )
        print("Trust score updated")
        
        # Keep the service running for a while
        await asyncio.sleep(5)
        
    finally:
        # Clean up
        await zeromesh.stop()
        print("ZeroMesh service stopped")

if __name__ == "__main__":
    asyncio.run(main()) 