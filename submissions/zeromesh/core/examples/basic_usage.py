"""
Basic example of using zeromesh for agent communication security
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from core.core import ZeroMesh
from core.config import ZeroMeshConfig, SSLConfig, MCPConfig, TrustConfig, AuditConfig
from core.policy import Policy

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

async def main():
    # Create test certificates directory
    certs_dir = Path("certs")
    certs_dir.mkdir(exist_ok=True)
    
    # Generate proper SSL certificates
    cert_path = certs_dir / "test.crt"
    key_path = certs_dir / "test.key"
    generate_test_certificates(cert_path, key_path)

    # Initialize ZeroMesh with proper configuration
    ssl_config = SSLConfig(
        cert_path=str(cert_path),
        key_path=str(key_path)
    )
    
    mcp_config = MCPConfig(
        host="localhost",
        port=3000,
        api_key="test_key"
    )
    
    trust_config = TrustConfig(
        score_threshold=0.7,
        decay_rate=0.1,
        quarantine_threshold=0.3
    )
    
    audit_config = AuditConfig(
        log_dir="logs",
        batch_size=100,
        flush_interval=60
    )
    
    config = ZeroMeshConfig(
        ssl=ssl_config,
        mcp=mcp_config,
        trust=trust_config,
        audit=audit_config
    )
    
    mesh = ZeroMesh()
    await mesh.initialize(config)
    
    try:
        # Add some example policies
        allow_all = Policy(
            id="allow_all",
            source_pattern=".*",  # Any source
            target_pattern=".*",  # Any target
            action_pattern="read|write",  # Allow read/write actions
            conditions={},
            priority=0,  # Lowest priority
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        await mesh.add_policy(allow_all)
        
        # Simulate some agent interactions
        agent1_id = "agent1"
        agent2_id = "agent2"
        
        # First interaction - should succeed
        message1 = {
            "action": "read",
            "data": "Hello from agent1!"
        }
        
        allowed = await mesh.verify_message(agent1_id, agent2_id, message1)
        print(f"Message 1 allowed: {allowed}")
        
        # Update trust scores based on interaction
        await mesh.update_trust_score(agent1_id, 0.8)  # Positive interaction
        await mesh.update_trust_score(agent2_id, 0.7)  # Positive interaction
        
        # Check trust scores
        agent1_score = await mesh.get_trust_score(agent1_id)
        agent2_score = await mesh.get_trust_score(agent2_id)
        
        print("\nTrust Scores:")
        print(f"Agent 1: {agent1_score:.2f}")
        print(f"Agent 2: {agent2_score:.2f}")
        
        # Simulate a malicious action
        message2 = {
            "action": "delete_all",  # Not allowed by policy
            "data": "Malicious payload"
        }
        
        allowed = await mesh.verify_message(agent1_id, agent2_id, message2)
        print(f"\nMalicious message allowed: {allowed}")
        
        # Update trust score negatively
        await mesh.update_trust_score(agent1_id, -0.5)  # Negative interaction
        
        # Check updated trust score
        agent1_score = await mesh.get_trust_score(agent1_id)
        print(f"\nAgent 1 trust score after violation: {agent1_score:.2f}")
        
        # Query audit logs
        print("\nAudit Logs:")
        logs = await mesh.get_audit_logs(
            start_time=datetime.utcnow() - timedelta(minutes=5)
        )
        print(json.dumps(logs, indent=2))
        
    finally:
        await mesh.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 