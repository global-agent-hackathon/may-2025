"""
Tests for core ZeroMesh functionality
"""
import pytest
import asyncio
from datetime import datetime, timedelta
import os
import tempfile
from typing import Dict, Any

from ..core import ZeroMesh
from ..config import ZeroMeshConfig
from ..aztp.protocol import AZTPConfig
from ..policy.engine import Policy

@pytest.fixture
async def zeromesh():
    """Create a test ZeroMesh instance"""
    # Create temp directory for keys
    with tempfile.TemporaryDirectory() as temp_dir:
        config = ZeroMeshConfig(
            aztp_config=AZTPConfig(
                key_dir=temp_dir,
                token_expiry=300  # 5 minutes
            ),
            min_trust_score=0.3
        )
        
        mesh = ZeroMesh()
        await mesh.initialize(config)
        yield mesh
        await mesh.cleanup()

@pytest.fixture
def test_cert():
    """Generate a test certificate"""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()
    
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return pem.decode()

@pytest.mark.asyncio
async def test_agent_registration(zeromesh, test_cert):
    """Test agent registration process"""
    agent_id = "test_agent_1"
    
    # Register agent
    await zeromesh.register_agent(agent_id, test_cert)
    
    # Verify registration
    status = await zeromesh.get_agent_status(agent_id)
    assert status.registered
    assert status.status == "active"
    
    # Verify initial trust score
    trust_score = await zeromesh.get_trust_score(agent_id)
    assert trust_score == 0.5  # Default neutral trust

@pytest.mark.asyncio
async def test_trust_relationships(zeromesh, test_cert):
    """Test trust relationship management"""
    agent_1 = "test_agent_1"
    agent_2 = "test_agent_2"
    
    # Register agents
    await zeromesh.register_agent(agent_1, test_cert)
    await zeromesh.register_agent(agent_2, test_cert)
    
    # Update trust relationship
    await zeromesh.update_trust_relationship(agent_1, agent_2, 0.8)
    
    # Verify trust scores
    trust_score = await zeromesh.get_trust_score(agent_2)
    assert trust_score == 0.8

@pytest.mark.asyncio
async def test_policy_enforcement(zeromesh, test_cert):
    """Test policy enforcement"""
    agent_id = "test_agent_1"
    await zeromesh.register_agent(agent_id, test_cert)
    
    # Add a policy
    policy = {
        "id": "test_policy_1",
        "agent_id": agent_id,
        "action": "read_data",
        "target": "test_resource",
        "effect": "allow",
        "conditions": {
            "trust_score": {"gte": 0.5}
        },
        "priority": 1
    }
    
    await zeromesh.policies.add_policy(policy)
    
    # Test permission check
    context = {"trust_score": 0.7}
    allowed = await zeromesh.policies.check_permission(
        agent_id,
        "read_data",
        "test_resource",
        context
    )
    assert allowed

@pytest.mark.asyncio
async def test_quarantine(zeromesh, test_cert):
    """Test agent quarantine functionality"""
    agent_id = "test_agent_1"
    await zeromesh.register_agent(agent_id, test_cert)
    
    # Quarantine agent
    await zeromesh.quarantine_agent(agent_id, "suspicious_activity")
    
    # Verify quarantine status
    status = await zeromesh.get_agent_status(agent_id)
    assert status.status == "quarantined"
    
    # Verify actions are blocked
    allowed = await zeromesh.verify_action(agent_id, "read_data")
    assert not allowed
    
    # Release from quarantine
    await zeromesh.release_from_quarantine(agent_id, "investigation_complete")
    
    # Verify status is restored
    status = await zeromesh.get_agent_status(agent_id)
    assert status.status == "active"

@pytest.mark.asyncio
async def test_audit_logging(zeromesh, test_cert):
    """Test audit logging"""
    agent_id = "test_agent_1"
    await zeromesh.register_agent(agent_id, test_cert)
    
    # Generate some audit events
    await zeromesh.log_audit_event("test_event", {
        "agent_id": agent_id,
        "action": "test_action"
    })
    
    # Query audit logs
    logs = await zeromesh.get_audit_logs(
        event_type="test_event",
        agent_id=agent_id
    )
    
    assert len(logs) == 1
    assert logs[0].type == "test_event"
    assert logs[0].agent_id == agent_id

@pytest.mark.asyncio
async def test_role_based_access(zeromesh, test_cert):
    """Test role-based access control"""
    agent_id = "test_agent_1"
    await zeromesh.register_agent(agent_id, test_cert)
    
    # Create role policy
    policy = {
        "id": "role_policy_1",
        "agent_id": "*",  # Applies to all agents with role
        "action": "admin_action",
        "effect": "allow",
        "conditions": {},
        "priority": 1
    }
    
    policy_obj = await zeromesh.policies.add_policy(policy)
    
    # Assign role and policy
    await zeromesh.policies.assign_role(agent_id, "admin")
    await zeromesh.policies.add_role_policy("admin", policy_obj.id)
    
    # Verify permission
    allowed = await zeromesh.policies.check_permission(agent_id, "admin_action")
    assert allowed

@pytest.mark.asyncio
async def test_system_metrics(zeromesh, test_cert):
    """Test system metrics collection"""
    # Register some agents
    for i in range(3):
        await zeromesh.register_agent(f"test_agent_{i}", test_cert)
        
    # Block one agent
    await zeromesh.block_agent("test_agent_1", "test_block")
    
    # Generate some audit logs
    for i in range(5):
        await zeromesh.log_audit_event("test_event", {"index": i})
        
    # Get metrics
    metrics = await zeromesh.get_system_metrics()
    
    assert metrics.active_agents == 3
    assert metrics.blocked_agents == 1
    assert metrics.total_audit_logs == 5
    assert isinstance(metrics.trust_graph_density, float)

if __name__ == "__main__":
    asyncio.run(test_core_functionality()) 