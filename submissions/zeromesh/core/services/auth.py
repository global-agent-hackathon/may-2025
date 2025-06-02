"""
Authentication service implementation
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        self._registry = None
        self._initialized = False
        self._agents = {}

    async def initialize(self, registry):
        """Initialize the authentication service"""
        if self._initialized:
            return
            
        self._registry = registry
        self._initialized = True
        logger.info("Authentication service initialized")

    async def cleanup(self):
        """Clean up resources"""
        self._initialized = False
        self._agents.clear()
        logger.info("Authentication service cleaned up")
        
    async def register_agent(self, agent_id: str, credentials: Dict[str, Any]):
        """Register an agent with credentials"""
        if not self._initialized:
            raise RuntimeError("Service not initialized")
            
        self._agents[agent_id] = credentials
        logger.info(f"Registered agent: {agent_id}")
        
    async def verify_agent(self, agent_id: str, token: str) -> bool:
        """Verify an agent's token"""
        if not self._initialized:
            raise RuntimeError("Service not initialized")
        
        if agent_id not in self._agents:
            return False
            
        stored_creds = self._agents[agent_id]
        return stored_creds.get("token") == token

    async def authenticate_agent(self, agent_id: str, cert_data: str) -> bool:
        """Authenticate an agent using its certificate"""
        if not self._initialized:
            raise RuntimeError("Service not initialized")
        
        if agent_id not in self._agents:
            logger.warning(f"Unknown agent {agent_id} attempted authentication")
            return False
            
        stored_creds = self._agents[agent_id]
        is_valid = stored_creds.get("cert") == cert_data
        
        if not is_valid:
            logger.warning(f"Invalid certificate provided for agent {agent_id}")
        else:
            logger.info(f"Agent {agent_id} authenticated successfully")
            
        return is_valid

    async def verify_client_cert(self, cert: dict) -> bool:
        """Verify a client certificate"""
        if not self._initialized:
            raise RuntimeError("Service not initialized")
        
        if not cert:
            logger.warning("No client certificate provided")
            return False
            
        # Extract Common Name from certificate
        logger.debug(f"Verifying client certificate: {cert}")
        logger.debug(f"Registered agents: {self._agents}")
        
        try:
            # Extract Common Name from subject
            subject = dict(cert.get('subject', []))
            cn = None
            for key, value in subject.items():
                if key[0] == 'commonName':
                    cn = value
                    break
            
            if not cn:
                logger.warning("Certificate missing Common Name")
                return False
                
            logger.debug(f"Found Common Name: {cn}")
            if not cn.startswith('agent:'):
                logger.warning("Certificate missing required agent prefix")
                return False
                
            agent_id = cn
            logger.debug(f"Extracted agent ID: {agent_id}")
            
            # Check if agent is registered
            if agent_id not in self._agents:
                logger.warning(f"Certificate from unregistered agent: {agent_id}")
                return False
                
            logger.info(f"Verified certificate for agent: {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error verifying certificate: {e}", exc_info=True)
            return False

    async def revoke_agent(self, agent_id: str):
        """Revoke an agent's registration"""
        if not self._initialized:
            raise RuntimeError("Service not initialized")
        
        if agent_id in self._agents:
            del self._agents[agent_id]
            logger.info(f"Agent {agent_id} registration revoked")
        else:
            logger.warning(f"Attempted to revoke unknown agent {agent_id}")

    def is_registered(self, agent_id: str) -> bool:
        """Check if an agent is registered"""
        if not self._initialized:
            raise RuntimeError("Service not initialized")
        return agent_id in self._agents 