"""
Tests for AZTP (Authenticated Zero Trust Protocol) functionality
"""

import pytest
import pytest_asyncio
import ssl
import logging
from pathlib import Path
from datetime import datetime, timedelta

from zeromesh.aztp_client import AZTPClient
from zeromesh.core import ZeroMesh
from zeromesh.config import ZeroMeshConfig, SSLConfig, MCPConfig, TrustConfig, AuditConfig

@pytest_asyncio.fixture
async def aztp_client(tmp_path):
    """Create a test AZTP client with temporary certificates"""
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization

    # Generate test certificates
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    
    cert = x509.CertificateBuilder().subject_name(
        x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, u"test-agent")])
    ).issuer_name(
        x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, u"test-ca")])
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=1)
    ).add_extension(
        x509.BasicConstraints(ca=False, path_length=None), critical=True
    ).sign(private_key, hashes.SHA256())

    # Save certificates
    cert_path = tmp_path / "test.crt"
    key_path = tmp_path / "test.key"
    
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    key_path.write_bytes(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

    # Create and return client
    client = AZTPClient(str(cert_path), str(key_path))
    await client.initialize()
    return client

@pytest.mark.asyncio
async def test_aztp_authentication(aztp_client):
    """Test AZTP authentication flow"""
    # Test valid credentials
    valid_creds = {
        "token": "valid_token",
        "cert": await aztp_client.get_cert_data()
    }
    assert await aztp_client.authenticate("test-agent", valid_creds)

    # Test invalid credentials
    invalid_creds = {
        "token": "invalid_token",
        "cert": "invalid_cert"
    }
    assert not await aztp_client.authenticate("test-agent", invalid_creds)

@pytest.mark.asyncio
async def test_aztp_verification(aztp_client):
    """Test AZTP agent verification"""
    # First authenticate
    creds = {
        "token": "test_token",
        "cert": await aztp_client.get_cert_data()
    }
    await aztp_client.authenticate("test-agent", creds)

    # Then verify
    assert await aztp_client.verify_agent("test-agent")
    assert not await aztp_client.verify_agent("unknown-agent")

@pytest.mark.asyncio
async def test_aztp_ssl_context(aztp_client):
    """Test AZTP SSL context configuration"""
    assert isinstance(aztp_client.ssl_context, ssl.SSLContext)
    assert aztp_client.ssl_context.verify_mode == ssl.CERT_REQUIRED

@pytest.mark.asyncio
async def test_aztp_cleanup(aztp_client):
    """Test AZTP client cleanup"""
    assert aztp_client.initialized
    await aztp_client.cleanup()
    assert not aztp_client.initialized 