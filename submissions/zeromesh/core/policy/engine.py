"""
Dynamic Policy Engine for ZeroMesh
"""
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class Policy(BaseModel):
    """Policy model"""
    id: str
    agent_id: str
    action: str
    target: Optional[str]
    effect: str  # "allow" or "deny"
    conditions: Dict[str, Any]
    priority: int
    created_at: datetime
    updated_at: datetime

class PolicyEngine:
    """
    Dynamic policy enforcement engine
    
    Features:
    - Role-based access control
    - Dynamic policy evaluation
    - Condition-based rules
    - Priority-based conflict resolution
    """
    
    def __init__(self):
        self.policies: Dict[str, Policy] = {}
        self.role_policies: Dict[str, List[str]] = {}  # role -> policy IDs
        self.agent_roles: Dict[str, Set[str]] = {}  # agent_id -> roles
        
    async def add_policy(self, policy_data: Dict[str, Any]) -> Policy:
        """Add a new policy"""
        policy = Policy(
            id=policy_data.get("id"),
            agent_id=policy_data.get("agent_id"),
            action=policy_data.get("action"),
            target=policy_data.get("target"),
            effect=policy_data.get("effect", "deny"),
            conditions=policy_data.get("conditions", {}),
            priority=policy_data.get("priority", 0),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.policies[policy.id] = policy
        return policy
        
    async def remove_policy(self, policy_id: str):
        """Remove a policy"""
        if policy_id in self.policies:
            del self.policies[policy_id]
            
    async def assign_role(self, agent_id: str, role: str):
        """Assign a role to an agent"""
        if agent_id not in self.agent_roles:
            self.agent_roles[agent_id] = set()
        self.agent_roles[agent_id].add(role)
        
    async def remove_role(self, agent_id: str, role: str):
        """Remove a role from an agent"""
        if agent_id in self.agent_roles:
            self.agent_roles[agent_id].discard(role)
            
    async def add_role_policy(self, role: str, policy_id: str):
        """Associate a policy with a role"""
        if role not in self.role_policies:
            self.role_policies[role] = []
        self.role_policies[role].append(policy_id)
        
    def _evaluate_conditions(self, conditions: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate policy conditions against context"""
        for key, expected in conditions.items():
            actual = context.get(key)
            
            if isinstance(expected, dict):
                # Handle operators
                op = list(expected.keys())[0]
                value = expected[op]
                
                if op == "gt" and not (actual > value):
                    return False
                elif op == "lt" and not (actual < value):
                    return False
                elif op == "gte" and not (actual >= value):
                    return False
                elif op == "lte" and not (actual <= value):
                    return False
                elif op == "in" and actual not in value:
                    return False
                elif op == "not" and actual == value:
                    return False
            elif actual != expected:
                return False
                
        return True
        
    async def check_permission(
        self,
        agent_id: str,
        action: str,
        target: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Check if an agent has permission to perform an action
        
        Args:
            agent_id: ID of the agent
            action: Action to perform
            target: Optional target of the action
            context: Additional context for condition evaluation
            
        Returns:
            bool indicating if the action is allowed
        """
        if context is None:
            context = {}
            
        # Get all applicable policies
        applicable_policies = []
        
        # Direct agent policies
        for policy in self.policies.values():
            if policy.agent_id == agent_id and policy.action == action:
                if target is None or policy.target is None or policy.target == target:
                    applicable_policies.append(policy)
                    
        # Role-based policies
        agent_roles = self.agent_roles.get(agent_id, set())
        for role in agent_roles:
            policy_ids = self.role_policies.get(role, [])
            for policy_id in policy_ids:
                policy = self.policies.get(policy_id)
                if policy and policy.action == action:
                    if target is None or policy.target is None or policy.target == target:
                        applicable_policies.append(policy)
                        
        if not applicable_policies:
            # No applicable policies - deny by default
            return False
            
        # Sort by priority (higher priority first)
        applicable_policies.sort(key=lambda p: p.priority, reverse=True)
        
        # Evaluate policies in priority order
        for policy in applicable_policies:
            if self._evaluate_conditions(policy.conditions, context):
                # First matching policy determines the outcome
                return policy.effect == "allow"
                
        # No matching policies - deny by default
        return False
        
    async def get_agent_permissions(self, agent_id: str) -> Set[str]:
        """Get all actions an agent is allowed to perform"""
        allowed_actions = set()
        
        # Check direct agent policies
        for policy in self.policies.values():
            if policy.agent_id == agent_id and policy.effect == "allow":
                allowed_actions.add(policy.action)
                
        # Check role-based policies
        agent_roles = self.agent_roles.get(agent_id, set())
        for role in agent_roles:
            policy_ids = self.role_policies.get(role, [])
            for policy_id in policy_ids:
                policy = self.policies.get(policy_id)
                if policy and policy.effect == "allow":
                    allowed_actions.add(policy.action)
                    
        return allowed_actions 