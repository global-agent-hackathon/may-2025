"""
Core ZeroMesh implementation
"""
from typing import Dict, Any, Optional, List, Set
import asyncio
from datetime import datetime
import networkx as nx
from pydantic import BaseModel, Field
import logging

from .config import ZeroMeshConfig
from .services.registry import ServiceRegistry
from .services.core import CoreService
from .services.auth import AuthService
from .services.trust import TrustService
from .services.audit import AuditService
from .aztp.protocol import AZTPProtocol
from .policy.engine import PolicyEngine

logger = logging.getLogger(__name__)

class AgentStatus(BaseModel):
    """Agent status model"""
    registered: bool = False
    status: str = "unknown"
    last_seen: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    trust_score: float = 0.0
    permissions: Set[str] = Field(default_factory=set)

class AuditLog(BaseModel):
    """Audit log entry model"""
    type: str
    timestamp: datetime
    agent_id: str
    data: Dict[str, Any]

class SystemMetrics(BaseModel):
    """System health metrics model"""
    active_agents: int = 0
    blocked_agents: int = 0
    total_audit_logs: int = 0
    uptime: str = "0:00:00"
    trust_graph_density: float = 0.0

class ZeroMesh:
    """Main ZeroMesh class"""
    
    def __init__(self):
        self.config: Optional[ZeroMeshConfig] = None
        self.registry = ServiceRegistry()
        self._initialized = False
        
        # Initialize state containers
        self.agents: Dict[str, AgentStatus] = {}
        self.policies = PolicyEngine()
        self.audit_logs: List[AuditLog] = []
        self.trust_graph = nx.DiGraph()  # Directed graph for trust relationships
        self.aztp = AZTPProtocol()
        
        # Track quarantined agents
        self.quarantined_agents: Set[str] = set()
        
    async def initialize(self, config: ZeroMeshConfig):
        """Initialize ZeroMesh with configuration"""
        if self._initialized:
            logger.warning("ZeroMesh already initialized")
            return
            
        logger.info("Initializing ZeroMesh")
        self.config = config
        self.registry._config = config  # Set config in registry
        
        # Register core services
        self.registry.register_service("core", CoreService)
        self.registry.register_service("auth", AuthService)
        self.registry.register_service("trust", TrustService)
        self.registry.register_service("audit", AuditService)
        
        # Initialize all services
        await self.registry.initialize_all_services()
        
        # Initialize AZTP protocol
        await self.aztp.initialize(config.aztp_config)
        
        self._initialized = True
        logger.info("ZeroMesh initialized successfully")
        
    async def cleanup(self):
        """Clean up resources"""
        if not self._initialized:
            return
            
        logger.info("Cleaning up ZeroMesh")
        await self.registry.cleanup()
        await self.aztp.cleanup()
        self._initialized = False
        
    @property
    def auth_service(self) -> AuthService:
        """Get the authentication service"""
        if not self._initialized:
            raise RuntimeError("ZeroMesh not initialized")
        core_service = self.registry.get_service("core")
        return core_service.auth_service
        
    @property
    def trust_service(self) -> TrustService:
        """Get the trust service"""
        if not self._initialized:
            raise RuntimeError("ZeroMesh not initialized")
        core_service = self.registry.get_service("core")
        return core_service.trust_service
        
    @property
    def audit_service(self) -> AuditService:
        """Get the audit service"""
        if not self._initialized:
            raise RuntimeError("ZeroMesh not initialized")
        core_service = self.registry.get_service("core")
        return core_service.audit_service

    async def register_agent(self, agent_id: str, cert_data: str):
        """Register a new agent with AZTP authentication"""
        if not self._initialized:
            raise RuntimeError("ZeroMesh not initialized")
            
        # Verify agent through AZTP
        auth_result = await self.aztp.authenticate_agent(agent_id, cert_data)
        if not auth_result.success:
            raise ValueError(f"Agent authentication failed: {auth_result.error}")
            
        # Register with auth service
        auth_service = self.auth_service
        await auth_service.register_agent(agent_id, auth_result.credentials)
        
        # Initialize agent status
        self.agents[agent_id] = AgentStatus(
            registered=True,
            status="active",
            last_seen=datetime.now(),
            permissions=auth_result.permissions
        )
        
        # Add to trust graph with initial neutral trust
        self.trust_graph.add_node(agent_id, trust_score=0.5)
        
        # Log registration
        await self.log_audit_event("agent_registered", {
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat()
        })

    async def verify_action(self, agent_id: str, action: str, target: Optional[str] = None) -> bool:
        """Verify if an agent can perform an action"""
        if not self._initialized:
            raise RuntimeError("ZeroMesh not initialized")
            
        # Check if agent is quarantined
        if agent_id in self.quarantined_agents:
            await self.log_audit_event("action_denied", {
                "agent_id": agent_id,
                "action": action,
                "reason": "agent_quarantined"
            })
            return False
            
        # Check trust score
        trust_score = await self.get_trust_score(agent_id)
        if trust_score < self.config.min_trust_score:
            await self.log_audit_event("action_denied", {
                "agent_id": agent_id,
                "action": action,
                "reason": "insufficient_trust"
            })
            return False
            
        # Check policy
        if not await self.policies.check_permission(agent_id, action, target):
            await self.log_audit_event("action_denied", {
                "agent_id": agent_id,
                "action": action,
                "reason": "policy_violation"
            })
            return False
            
        return True

    async def update_trust_relationship(self, source: str, target: str, trust_score: float):
        """Update trust relationship between agents"""
        if not self._initialized:
            raise RuntimeError("ZeroMesh not initialized")
            
        # Update trust graph
        self.trust_graph.add_edge(source, target, trust_score=trust_score)
        
        # Update agent's overall trust score
        await self.update_trust_score(target, self._calculate_agent_trust(target))
        
        # Log trust update
        await self.log_audit_event("trust_updated", {
            "source": source,
            "target": target,
            "trust_score": trust_score
        })

    def _calculate_agent_trust(self, agent_id: str) -> float:
        """Calculate overall trust score for an agent based on graph"""
        if not self.trust_graph.has_node(agent_id):
            return 0.0
            
        incoming_edges = self.trust_graph.in_edges(agent_id, data=True)
        if not incoming_edges:
            return 0.5  # Default neutral trust
            
        # Weight trust scores by source agent's own trust
        weighted_scores = []
        for source, _, data in incoming_edges:
            source_trust = self.trust_graph.nodes[source].get("trust_score", 0.5)
            weighted_scores.append(data["trust_score"] * source_trust)
            
        return sum(weighted_scores) / len(weighted_scores)

    async def quarantine_agent(self, agent_id: str, reason: str):
        """Place an agent in quarantine"""
        if not self._initialized:
            raise RuntimeError("ZeroMesh not initialized")
            
        self.quarantined_agents.add(agent_id)
        agent = self.agents.get(agent_id)
        if agent:
            agent.status = "quarantined"
            
        await self.log_audit_event("agent_quarantined", {
            "agent_id": agent_id,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })

    async def release_from_quarantine(self, agent_id: str, reason: str):
        """Release an agent from quarantine"""
        if not self._initialized:
            raise RuntimeError("ZeroMesh not initialized")
            
        self.quarantined_agents.discard(agent_id)
        agent = self.agents.get(agent_id)
        if agent:
            agent.status = "active"
            
        await self.log_audit_event("agent_released", {
            "agent_id": agent_id,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })

    async def get_agent_status(self, agent_id: str) -> AgentStatus:
        """Get the current status of an agent"""
        return self.agents.get(agent_id, AgentStatus())

    async def update_trust_score(self, agent_id: str, score: float):
        """Update trust score for an agent"""
        if not self._initialized:
            raise RuntimeError("ZeroMesh not initialized")
            
        trust_service = self.trust_service
        await trust_service.update_trust_score(agent_id, score)
        self.trust_scores[agent_id] = score

    async def get_trust_score(self, agent_id: str) -> float:
        """Get the trust score for an agent"""
        if not self._initialized:
            raise RuntimeError("ZeroMesh not initialized")
            
        trust_service = self.trust_service
        return await trust_service.get_trust_score(agent_id)

    async def add_policy(self, policy: Dict[str, Any]):
        """Add a new policy"""
        if not self._initialized:
            raise RuntimeError("ZeroMesh not initialized")
            
        self.policies[policy["agent_id"]] = policy

    async def get_policies(self) -> Dict[str, Any]:
        """Get all active policies"""
        return self.policies

    async def log_audit_event(self, event_type: str, data: Dict[str, Any]):
        """Log an audit event"""
        if not self._initialized:
            raise RuntimeError("ZeroMesh not initialized")
            
        audit_service = self.audit_service
        await audit_service.log_event(event_type, data)
        
        # Also store in local list for quick access
        self.audit_logs.append(AuditLog(
            type=event_type,
            timestamp=datetime.now(),
            agent_id=data.get("agent_id", "system"),
            data=data
        ))

    async def get_audit_logs(
        self,
        event_type: Optional[str] = None,
        agent_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[AuditLog]:
        """Query audit logs with filters"""
        filtered_logs = self.audit_logs
        
        if event_type:
            filtered_logs = [log for log in filtered_logs if log.type == event_type]
        
        if agent_id:
            filtered_logs = [log for log in filtered_logs if log.agent_id == agent_id]
        
        if start_time:
            filtered_logs = [log for log in filtered_logs if log.timestamp >= start_time]
        
        if end_time:
            filtered_logs = [log for log in filtered_logs if log.timestamp <= end_time]
        
        return filtered_logs

    async def block_agent(self, agent_id: str, reason: str):
        """Block an agent"""
        self.policies[agent_id] = {
            "action": "block",
            "reason": reason,
            "timestamp": datetime.utcnow()
        }
        self.audit_logs.append(AuditLog(
            type="agent_blocked",
            agent_id=agent_id,
            reason=reason
        ))

    async def get_system_metrics(self) -> SystemMetrics:
        """Get system health metrics"""
        return SystemMetrics(
            active_agents=len(self.agents),
            blocked_agents=len([p for p in self.policies.values() if p["action"] == "block"]),
            total_audit_logs=len(self.audit_logs),
            trust_graph_density=nx.density(self.trust_graph)
        ) 