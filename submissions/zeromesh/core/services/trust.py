"""
Trust service implementation
"""
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class TrustService:
    def __init__(self):
        self._registry = None
        self._initialized = False
        self._trust_scores = {}
        self._quarantined_agents = set()
        self.quarantine_threshold = 0.3  # Trust score below this triggers quarantine
        
    async def initialize(self, registry):
        """Initialize the trust service"""
        if self._initialized:
            return
            
        self._registry = registry
        self._initialized = True
        logger.info("Trust service initialized")
        
    async def cleanup(self):
        """Clean up resources"""
        self._initialized = False
        self._trust_scores.clear()
        self._quarantined_agents.clear()
        logger.info("Trust service cleaned up")
        
    async def update_trust_score(self, agent_id: str, score: float):
        """Update an agent's trust score"""
        if not self._initialized:
            raise RuntimeError("Service not initialized")
            
        score = max(0.0, min(1.0, score))  # Clamp between 0 and 1
        self._trust_scores[agent_id] = score
        
        # Check if agent should be quarantined
        if score < self.quarantine_threshold:
            self._quarantined_agents.add(agent_id)
            logger.warning(f"Agent {agent_id} quarantined due to low trust score: {score}")
        elif agent_id in self._quarantined_agents:
            self._quarantined_agents.remove(agent_id)
            logger.info(f"Agent {agent_id} removed from quarantine, trust score: {score}")
            
    async def get_trust_score(self, agent_id: str) -> float:
        """Get an agent's trust score"""
        if not self._initialized:
            raise RuntimeError("Service not initialized")
            
        return self._trust_scores.get(agent_id, 0.5)  # Default to neutral trust
        
    def is_quarantined(self, agent_id: str) -> bool:
        """Check if an agent is quarantined"""
        if not self._initialized:
            raise RuntimeError("Service not initialized")
            
        return agent_id in self._quarantined_agents 