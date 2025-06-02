"""
Integration tests for SSL authentication and agent communication
"""

import pytest
import pytest_asyncio
import asyncio
import ssl
import logging
from pathlib import Path
from core.utils.ssl_utils import (
    generate_ca_certificate,
    generate_server_certificate,
    generate_client_certificate
)
from core.config import ZeroMeshConfig, SSLConfig, MCPConfig, TrustConfig, AuditConfig
from core.core import ZeroMesh
from core.services.auth import AuthService

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture
def cert_dir(tmp_path):
    """Create a temporary directory for certificates"""
    return tmp_path / "certs"

@pytest.fixture
def ssl_setup(cert_dir):
    """Set up SSL certificates"""
    # Generate CA certificate
    ca_cert_path, ca_key_path = generate_ca_certificate(cert_dir)
    
    # Generate server certificate
    server_cert_path, server_key_path = generate_server_certificate(
        cert_dir,
        ca_cert_path,
        ca_key_path,
        dns_names=["localhost"]
    )
    
    # Generate client certificates
    client1_cert_path, client1_key_path = generate_client_certificate(
        cert_dir,
        ca_cert_path,
        ca_key_path,
        "agent:agent1"  # Use proper agent prefix
    )
    
    client2_cert_path, client2_key_path = generate_client_certificate(
        cert_dir,
        ca_cert_path,
        ca_key_path,
        "agent:agent2"  # Use proper agent prefix
    )
    
    return {
        "ca": (ca_cert_path, ca_key_path),
        "server": (server_cert_path, server_key_path),
        "client1": (client1_cert_path, client1_key_path),
        "client2": (client2_cert_path, client2_key_path)
    }

@pytest_asyncio.fixture
async def zeromesh_server(ssl_setup):
    """Create and initialize a ZeroMesh server instance"""
    config = ZeroMeshConfig(
        ssl=SSLConfig(
            cert_path=str(ssl_setup["server"][0]),
            key_path=str(ssl_setup["server"][1]),
            ca_path=str(ssl_setup["ca"][0])
        ),
        mcp=MCPConfig(
            host="localhost",
            port=8443,
            api_key="test_key"
        ),
        trust=TrustConfig(
            score_threshold=0.7,
            decay_rate=0.1,
            quarantine_threshold=0.3
        ),
        audit=AuditConfig(
            log_dir="logs",
            batch_size=100,
            flush_interval=60
        )
    )
    
    server = ZeroMesh()
    await server.initialize(config)
    yield server
    await server.cleanup()

async def create_client_context(cert_path, key_path, ca_path):
    """Create an SSL context for a client"""
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_cert_chain(cert_path, key_path)
    context.load_verify_locations(cafile=ca_path)
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED
    return context

class SSLHandler:
    """Handler for SSL connections"""
    
    def __init__(self, auth_service):
        self.auth_service = auth_service
    
    async def handle_client(self, reader, writer):
        """Handle client connection"""
        try:
            logger.debug("Handling new client connection")
            # Get client certificate
            transport = writer.transport
            ssl_object = transport.get_extra_info('ssl_object')
            logger.debug(f"SSL object: {ssl_object}")
            
            response_sent = False
            try:
                if ssl_object:
                    cert = ssl_object.getpeercert()
                    logger.debug(f"Received client certificate: {cert}")
                    if cert:
                        logger.debug("Verifying client certificate")
                        is_verified = await self.auth_service.verify_client_cert(cert)
                        logger.debug(f"Certificate verification result: {is_verified}")
                        if is_verified:
                            # Send success message
                            logger.debug("Sending OK response")
                            writer.write(b'OK')
                            await writer.drain()
                            response_sent = True
                            logger.debug("Response sent successfully")
                            return
                        else:
                            logger.debug("Certificate verification failed")
                    else:
                        logger.debug("No client certificate received")
                else:
                    logger.debug("No SSL object found")
            finally:
                if not response_sent:
                    logger.debug("Closing connection without sending OK")
                    writer.write(b'ERROR')
                await writer.drain()
                writer.close()
                await writer.wait_closed()
                logger.debug("Connection closed")
                
        except Exception as e:
            logger.error(f"Error handling client: {e}", exc_info=True)
            try:
                writer.close()
                await writer.wait_closed()
            except:
                pass  # Ignore errors during emergency cleanup

@pytest.mark.asyncio
async def test_ssl_authentication(zeromesh_server, ssl_setup):
    """Test SSL authentication between server and client"""
    # Get the server's SSL context
    server_context = zeromesh_server.auth_service.get_ssl_context()
    assert server_context is not None
    
    # Register agent1
    client1_cert_data = ssl_setup["client1"][0].read_text()
    logger.debug(f"Client certificate data: {client1_cert_data}")
    await zeromesh_server.auth_service.register_agent("agent:agent1", client1_cert_data)  # Use proper agent ID
    
    # Verify registration
    assert zeromesh_server.auth_service.is_registered("agent:agent1")
    logger.debug(f"Registered agents: {zeromesh_server.auth_service._registered_agents}")
    
    # Create client SSL context
    client_context = await create_client_context(
        ssl_setup["client1"][0],
        ssl_setup["client1"][1],
        ssl_setup["ca"][0]
    )
    
    # Create SSL handler
    handler = SSLHandler(zeromesh_server.auth_service)
    
    # Create server and client sockets
    server = await asyncio.start_server(
        handler.handle_client,  # Use our handler
        "localhost",
        0,  # Let OS choose port
        ssl=server_context
    )
    port = server.sockets[0].getsockname()[1]
    
    try:
        # Test successful connection with registered agent
        reader, writer = await asyncio.open_connection(
            "localhost",
            port,
            ssl=client_context
        )
        response = await reader.read(2)
        assert response == b'OK'
        writer.close()
        await writer.wait_closed()
        
        # Test connection with unregistered agent (should fail)
        bad_context = await create_client_context(
            ssl_setup["client2"][0],  # Use different client cert
            ssl_setup["client2"][1],
            ssl_setup["ca"][0]
        )
        
        # This should raise an SSL error or connection will be closed
        with pytest.raises((ssl.SSLCertVerificationError, ssl.SSLError, ConnectionRefusedError, ConnectionResetError)):
            reader, writer = await asyncio.open_connection(
                "localhost",
                port,
                ssl=bad_context
            )
            response = await reader.read(2)  # This should fail
    
    finally:
        server.close()
        await server.wait_closed()

@pytest.mark.asyncio
async def test_agent_registration(zeromesh_server, ssl_setup):
    """Test agent registration and authentication"""
    # Read client certificate data
    client_cert_data = ssl_setup["client1"][0].read_text()
    
    # Register agent
    await zeromesh_server.auth_service.register_agent("agent:agent1", client_cert_data)  # Use proper agent ID
    
    # Verify registration
    assert zeromesh_server.auth_service.is_registered("agent:agent1")  # Use proper agent ID
    
    # Test authentication
    assert await zeromesh_server.auth_service.authenticate_agent("agent:agent1", client_cert_data)  # Use proper agent ID
    
    # Test authentication with wrong cert
    wrong_cert_data = ssl_setup["client2"][0].read_text()
    assert not await zeromesh_server.auth_service.authenticate_agent("agent:agent1", wrong_cert_data)  # Use proper agent ID
    
    # Test revocation
    await zeromesh_server.auth_service.revoke_agent("agent:agent1")  # Use proper agent ID
    assert not zeromesh_server.auth_service.is_registered("agent:agent1")  # Use proper agent ID

@pytest.mark.asyncio
async def test_trust_scoring(zeromesh_server):
    """Test trust scoring functionality"""
    # Register an agent
    agent_id = "test_agent"
    initial_score = await zeromesh_server.trust_service.get_trust_score(agent_id)
    assert initial_score == 1.0  # Default trust score
    
    # Update trust score
    new_score = await zeromesh_server.trust_service.update_trust_score(agent_id, -0.3)
    assert new_score == 0.7
    
    # Check quarantine
    assert not zeromesh_server.trust_service.is_quarantined(agent_id)
    
    # Update to quarantine threshold
    await zeromesh_server.trust_service.update_trust_score(agent_id, -0.5)
    assert zeromesh_server.trust_service.is_quarantined(agent_id) 