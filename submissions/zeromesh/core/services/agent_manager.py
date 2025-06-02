"""
Agent manager service for handling agent states and blocking
"""

import asyncio
from typing import Dict, Any, Optional, Set
from datetime import datetime
import logging

from ..config import ZeroMeshConfig
from .audit import AuditService, AuditEvent
from .trust import TrustService

logger = logging.getLogger(__name__)

class AgentState:
    """Represents an agent's current state"""
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.status = "inactive"  # inactive, active, blocked, quarantined
        self.last_seen = None
        self.block_reason = None
        self.quarantine_reason = None
        self.metadata: Dict[str, Any] = {}

class AgentManager:
    """Service for managing agent states and blocking"""
    
    def __init__(self, config: ZeroMeshConfig, trust_service: TrustService, audit_service: AuditService):
        self.config = config
        self.trust_service = trust_service
        self.audit_service = audit_service
        self.agents: Dict[str, AgentState] = {}
        self.initialized = False

    async def initialize(self):
        """Initialize the agent manager"""
        self.initialized = True
        logger.info("Agent manager initialized")

    async def register_agent(self, agent_id: str, metadata: Dict[str, Any]) -> bool:
        """Register a new agent"""
        if not self.initialized:
            raise RuntimeError("Agent manager not initialized")

        try:
            # Create new agent state
            agent = AgentState(agent_id)
            agent.status = "active"
            agent.last_seen = datetime.utcnow()
            agent.metadata = metadata

            self.agents[agent_id] = agent

            # Log registration
            await self.audit_service.log_event(AuditEvent(
                "agent_registered",
                agent_id,
                {"metadata": metadata}
            ))

            logger.info(f"Agent {agent_id} registered successfully")
            return True

        except Exception as e:
            logger.error(f"Error registering agent {agent_id}: {e}")
            return False

    async def block_agent(self, agent_id: str, reason: str) -> bool:
        """Block an agent"""
        if not self.initialized:
            raise RuntimeError("Agent manager not initialized")

        try:
            if agent_id not in self.agents:
                logger.warning(f"Attempted to block unknown agent {agent_id}")
                return False

            agent = self.agents[agent_id]
            agent.status = "blocked"
            agent.block_reason = reason

            # Log blocking event
            await self.audit_service.log_event(AuditEvent(
                "agent_blocked",
                agent_id,
                {"reason": reason}
            ))

            # Update trust score
            await self.trust_service.update_trust_score(agent_id, -1.0)

            logger.info(f"Agent {agent_id} blocked: {reason}")
            return True

        except Exception as e:
            logger.error(f"Error blocking agent {agent_id}: {e}")
            return False

    async def quarantine_agent(self, agent_id: str, reason: str) -> bool:
        """Quarantine an agent"""
        if not self.initialized:
            raise RuntimeError("Agent manager not initialized")

        try:
            if agent_id not in self.agents:
                logger.warning(f"Attempted to quarantine unknown agent {agent_id}")
                return False

            agent = self.agents[agent_id]
            agent.status = "quarantined"
            agent.quarantine_reason = reason

            # Log quarantine event
            await self.audit_service.log_event(AuditEvent(
                "agent_quarantined",
                agent_id,
                {"reason": reason}
            ))

            logger.info(f"Agent {agent_id} quarantined: {reason}")
            return True

        except Exception as e:
            logger.error(f"Error quarantining agent {agent_id}: {e}")
            return False

    async def release_agent(self, agent_id: str) -> bool:
        """Release an agent from blocked/quarantined state"""
        if not self.initialized:
            raise RuntimeError("Agent manager not initialized")

        try:
            if agent_id not in self.agents:
                logger.warning(f"Attempted to release unknown agent {agent_id}")
                return False

            agent = self.agents[agent_id]
            prev_status = agent.status
            agent.status = "active"
            agent.block_reason = None
            agent.quarantine_reason = None

            # Log release event
            await self.audit_service.log_event(AuditEvent(
                "agent_released",
                agent_id,
                {"previous_status": prev_status}
            ))

            logger.info(f"Agent {agent_id} released from {prev_status} state")
            return True

        except Exception as e:
            logger.error(f"Error releasing agent {agent_id}: {e}")
            return False

    async def update_agent_status(self, agent_id: str, status: str) -> bool:
        """Update an agent's status"""
        if not self.initialized:
            raise RuntimeError("Agent manager not initialized")

        try:
            if agent_id not in self.agents:
                logger.warning(f"Attempted to update unknown agent {agent_id}")
                return False

            agent = self.agents[agent_id]
            old_status = agent.status
            agent.status = status
            agent.last_seen = datetime.utcnow()

            # Log status change
            if old_status != status:
                await self.audit_service.log_event(AuditEvent(
                    "agent_status_changed",
                    agent_id,
                    {
                        "old_status": old_status,
                        "new_status": status
                    }
                ))

            logger.info(f"Agent {agent_id} status updated to {status}")
            return True

        except Exception as e:
            logger.error(f"Error updating agent {agent_id} status: {e}")
            return False

    def get_agent_state(self, agent_id: str) -> Optional[AgentState]:
        """Get the current state of an agent"""
        if not self.initialized:
            raise RuntimeError("Agent manager not initialized")
        return self.agents.get(agent_id)

    async def cleanup(self):
        """Clean up resources"""
        self.initialized = False
        self.agents.clear()
        logger.info("Agent manager cleaned up") 