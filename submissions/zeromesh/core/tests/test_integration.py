"""
Integration tests for ZeroMesh core functionality
"""

import asyncio
import pytest
import pytest_asyncio
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Any
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import datetime as dt

from core.core import ZeroMesh
from core.config import ZeroMeshConfig, SSLConfig, TrustConfig, MCPConfig, AuditConfig
from core.services.registry import ServiceRegistry
from core.services.core import CoreService
from core.services.auth import AuthService
from core.services.trust import TrustService
from core.services.audit import AuditService
from core.mem0ai import Mem0Client

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_test_certificates(cert_path: Path, key_path: Path):
    """Generate test SSL certificates"""
    # Generate key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    
    # Generate certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"ZeroMesh Test"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, u"Testing"),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=10)
    ).add_extension(
        x509.SubjectAlternativeName([x509.DNSName(u"localhost")]),
        critical=False,
    ).sign(private_key, hashes.SHA256())
    
    # Save certificate and key
    cert_path.parent.mkdir(parents=True, exist_ok=True)
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    key_path.write_bytes(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

@pytest_asyncio.fixture
async def config():
    """Create a test configuration"""
    # Generate test certificates
    cert_path = Path("test_certs/test.crt")
    key_path = Path("test_certs/test.key")
    generate_test_certificates(cert_path, key_path)
    
    ssl_config = SSLConfig(
        cert_path=str(cert_path),
        key_path=str(key_path)
    )
    
    mcp_config = MCPConfig(
        host="localhost",
        port=8443,
        api_key="test_key"  # Add test API key
    )
    
    trust_config = TrustConfig(
        score_threshold=0.7,
        decay_rate=0.1,
        quarantine_threshold=0.3
    )
    
    # Create test log directory
    log_dir = Path("test_logs")
    log_dir.mkdir(exist_ok=True)
    
    audit_config = AuditConfig(
        log_dir=str(log_dir),
        batch_size=10,  # Small batch size for testing
        flush_interval=1  # Short interval for testing
    )
    
    return ZeroMeshConfig(
        ssl=ssl_config,
        trust=trust_config,
        mcp=mcp_config,
        audit=audit_config
    )

@pytest_asyncio.fixture
async def service_registry(config):
    """Create and initialize service registry"""
    registry = ServiceRegistry(config)
    registry.register_service_type("core", CoreService)
    registry.register_service_type("auth", AuthService)
    registry.register_service_type("trust", TrustService)
    registry.register_service_type("audit", AuditService)
    
    # Initialize all services
    await registry.initialize_service("core")
    await registry.initialize_service("auth")
    await registry.initialize_service("trust")
    await registry.initialize_service("audit")
    
    return registry

@pytest.mark.asyncio
async def test_service_initialization(service_registry):
    """Test service initialization"""
    logger.info("Testing service initialization...")
    
    # Services are already initialized in the fixture
    core_service = service_registry.get_service("core")
    assert core_service.initialized
    
    auth_service = service_registry.get_service("auth")
    trust_service = service_registry.get_service("trust")
    audit_service = service_registry.get_service("audit")
    
    assert auth_service.initialized
    assert trust_service.initialized
    assert audit_service.initialized

@pytest.mark.asyncio
async def test_trust_scoring(service_registry):
    """Test trust scoring functionality"""
    logger.info("Testing trust scoring...")
    
    trust_service = service_registry.get_service("trust")
    
    # Test initial trust score
    agent_id = "test_agent"
    score = await trust_service.get_trust_score(agent_id)
    assert 0.0 <= score <= 1.0
    
    # Test trust score update
    await trust_service.update_trust_score(agent_id, 0.8)
    new_score = await trust_service.get_trust_score(agent_id)
    assert new_score == 0.8
    
    # Test trust score decay
    await asyncio.sleep(1)  # Wait for decay
    decayed_score = await trust_service.get_trust_score(agent_id)
    assert decayed_score < new_score

@pytest.mark.asyncio
async def test_audit_logging(service_registry):
    """Test audit logging functionality"""
    logger.info("Testing audit logging...")
    
    audit_service = service_registry.get_service("audit")
    
    # Test event logging
    event_data = {
        "agent_id": "test_agent",
        "action": "test_action",
        "status": "success"
    }
    await audit_service.log_event("test_event", event_data)
    
    # Test log retrieval
    now = datetime.now(timezone.utc)
    logs = await audit_service.get_logs(
        event_type="test_event",
        agent_id="test_agent",
        start_time=now - timedelta(minutes=5),
        end_time=now + timedelta(minutes=5)
    )
    
    assert len(logs) > 0
    assert logs[0]["type"] == "test_event"
    assert logs[0]["details"]["agent_id"] == "test_agent"

@pytest.mark.asyncio
async def test_auth_service(service_registry):
    """Test authentication service"""
    logger.info("Testing authentication service...")
    
    auth_service = service_registry.get_service("auth")
    
    # Test agent registration
    agent_id = "test_agent"
    agent_cert = "test_cert_data"
    await auth_service.register_agent(agent_id, agent_cert)
    
    # Test agent authentication
    is_authenticated = await auth_service.authenticate_agent(agent_id, agent_cert)
    assert is_authenticated
    
    # Test invalid authentication
    is_authenticated = await auth_service.authenticate_agent(agent_id, "wrong_cert")
    assert not is_authenticated

@pytest.mark.asyncio
async def test_mem0_integration(service_registry):
    """Test Mem0 integration"""
    logger.info("Testing Mem0 integration...")
    
    audit_service = service_registry.get_service("audit")
    mem0_client = audit_service._mem0_client
    
    # Test Mem0 logging with fallback
    test_data = {
        "event": "test_mem0",
        "timestamp": datetime.now().isoformat(),
        "data": {"test": "data"}
    }
    
    # Log event (should work even if Mem0 API is down due to fallback)
    await mem0_client.store("test_collection", test_data)
    
    # Query logs
    logs = await mem0_client.query(
        "test_collection",
        {"event": "test_mem0"}
    )
    
    assert len(logs) > 0
    assert logs[0]["event"] == "test_mem0"

@pytest.mark.asyncio
async def test_full_workflow(config):
    """Test complete workflow"""
    logger.info("Testing complete workflow...")
    
    # Initialize ZeroMesh with config
    mesh = ZeroMesh()
    await mesh.initialize(config)
    
    # Register test agent
    agent_id = "test_workflow_agent"
    await mesh.register_agent(agent_id, "test_cert")
    
    # Verify agent status
    status = await mesh.get_agent_status(agent_id)
    assert status.registered
    
    # Update trust score
    await mesh.update_trust_score(agent_id, 0.9)
    score = await mesh.get_trust_score(agent_id)
    assert score == 0.9
    
    # Create test policy
    policy = {
        "agent_id": agent_id,
        "permissions": ["read", "write"],
        "conditions": {"min_trust_score": 0.8}
    }
    await mesh.add_policy(policy)
    
    # Verify policy
    policies = await mesh.get_policies()
    assert agent_id in policies
    
    # Test audit logging
    await mesh.log_audit_event("workflow_test", {
        "agent_id": agent_id,
        "action": "complete_workflow",
        "status": "success"
    })
    
    # Query audit logs
    logs = await mesh.get_audit_logs(
        event_type="workflow_test",
        agent_id=agent_id
    )
    assert len(logs) > 0

if __name__ == "__main__":
    """Run tests directly"""
    asyncio.run(pytest.main([__file__, "-v"])) 