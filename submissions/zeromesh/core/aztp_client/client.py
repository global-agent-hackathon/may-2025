"""
AZTP client implementation for secure agent communication
"""

import ssl
import asyncio
from typing import Dict, Any, Optional, Set
import logging

logger = logging.getLogger(__name__)

class AZTPClient:
    """
    Client for the Authenticated Zero Trust Protocol (AZTP)
    Handles secure communication between agents
    """

    def __init__(self, cert_path: str, key_path: str):
        self.cert_path = cert_path
        self.key_path = key_path
        self.ssl_context = None
        self.initialized = False
        self._cert_data = None
        self._authenticated_agents: Set[str] = set()

    async def initialize(self):
        """Initialize the SSL context and other resources"""
        try:
            self.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            self.ssl_context.verify_mode = ssl.CERT_REQUIRED
            self.ssl_context.load_cert_chain(self.cert_path, self.key_path)
            
            # Load certificate data
            with open(self.cert_path, 'rb') as f:
                self._cert_data = f.read().decode('utf-8')
                
            self.initialized = True
            logger.info("AZTP client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AZTP client: {e}")
            raise

    async def get_cert_data(self) -> str:
        """Get the client's certificate data"""
        if not self.initialized:
            raise RuntimeError("AZTP client not initialized")
        return self._cert_data

    async def authenticate(self, agent_id: str, credentials: Dict[str, Any]) -> bool:
        """
        Authenticate an agent using provided credentials
        Returns True if authentication is successful, False otherwise
        """
        if not self.initialized:
            raise RuntimeError("AZTP client not initialized")

        try:
            # Verify certificate
            cert_valid = (
                isinstance(credentials.get("cert"), str) and
                credentials["cert"].strip() == self._cert_data.strip()
            )
            
            # Verify token
            token_valid = (
                isinstance(credentials.get("token"), str) and 
                len(credentials.get("token", "")) > 0
            )
            
            is_valid = cert_valid and token_valid
            
            if is_valid:
                logger.info(f"Agent {agent_id} authenticated successfully")
                self._authenticated_agents.add(agent_id)
            else:
                logger.warning(f"Authentication failed for agent {agent_id}")
                self._authenticated_agents.discard(agent_id)
            
            return is_valid

        except Exception as e:
            logger.error(f"Authentication error for agent {agent_id}: {e}")
            return False

    async def verify_agent(self, agent_id: str) -> bool:
        """Verify if an agent is currently authenticated"""
        if not self.initialized:
            raise RuntimeError("AZTP client not initialized")
        return agent_id in self._authenticated_agents

    async def cleanup(self):
        """Clean up resources"""
        self.initialized = False
        self._authenticated_agents.clear()
        logger.info("AZTP client cleaned up") 