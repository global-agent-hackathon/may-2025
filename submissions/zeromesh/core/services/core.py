"""
Core service for orchestrating ZeroMesh functionality
"""

import logging
from typing import Optional, Dict, Any
from .base import BaseService
from .auth import AuthService
from .trust import TrustService
from .audit import AuditService, AuditEvent

logger = logging.getLogger(__name__)

class CoreService:
    def __init__(self):
        self._registry = None
        self._initialized = False
        
    async def initialize(self, registry):
        """Initialize the core service"""
        if self._initialized:
            return
            
        self._registry = registry
        self._initialized = True
        logger.info("Core service initialized")
        
    async def cleanup(self):
        """Clean up resources"""
        self._initialized = False
        logger.info("Core service cleaned up")
        
    @property
    def auth_service(self):
        """Get the authentication service"""
        if not self._initialized:
            raise RuntimeError("Service not initialized")
        return self._registry.get_service("auth")
        
    @property
    def trust_service(self):
        """Get the trust service"""
        if not self._initialized:
            raise RuntimeError("Service not initialized")
        return self._registry.get_service("trust")
        
    @property
    def audit_service(self):
        """Get the audit service"""
        if not self._initialized:
            raise RuntimeError("Service not initialized")
        return self._registry.get_service("audit")
        
    async def register_agent(self, agent_id: str, credentials: dict):
        """Register a new agent"""
        if not self._initialized:
            raise RuntimeError("Service not initialized")
            
        await self.auth_service.register_agent(agent_id, credentials)
        await self.trust_service.update_trust_score(agent_id, 0.5)  # Initial neutral trust
        await self.audit_service.log_event("agent_registered", {
            "agent_id": agent_id,
            "initial_trust": 0.5
        })

    async def handle_message(self, agent_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an incoming message from an agent"""
        self._check_initialized()
        
        # Check if agent is quarantined
        if self._trust_service.is_quarantined(agent_id):
            await self._audit_service.log_event("message_rejected", {
                "agent_id": agent_id,
                "reason": "quarantined",
                "trust_score": await self._trust_service.get_trust_score(agent_id),
                "immutable": True
            })
            raise ValueError(f"Agent {agent_id} is quarantined")
        
        # Process message and update trust score based on result
        try:
            # TODO: Add message processing logic here
            result = {"status": "success"}
            
            # Update trust score positively
            old_score = await self._trust_service.get_trust_score(agent_id)
            await self._trust_service.update_trust_score(agent_id, 0.1)
            new_score = await self._trust_service.get_trust_score(agent_id)
            
            await self._audit_service.log_event("message_processed", {
                "agent_id": agent_id,
                "success": True,
                "trust_score": {
                    "old": old_score,
                    "new": new_score,
                    "delta": 0.1
                },
                "immutable": True
            })
            
            return result
            
        except Exception as e:
            # Update trust score negatively
            old_score = await self._trust_service.get_trust_score(agent_id)
            await self._trust_service.update_trust_score(agent_id, -0.2)
            new_score = await self._trust_service.get_trust_score(agent_id)
            
            await self._audit_service.log_event("message_processed", {
                "agent_id": agent_id,
                "success": False,
                "error": str(e),
                "trust_score": {
                    "old": old_score,
                    "new": new_score,
                    "delta": -0.2
                },
                "immutable": True
            })
            
            raise

    @property
    def running(self) -> bool:
        """Check if service is running"""
        return self._running 

    @property
    def auth_service(self) -> AuthService:
        """Get the authentication service"""
        return self._auth_service

    @property
    def trust_service(self) -> TrustService:
        """Get the trust service"""
        return self._trust_service

    @property
    def audit_service(self) -> AuditService:
        """Get the audit service"""
        return self._audit_service 