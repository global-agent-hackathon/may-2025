"""
Tests for agent manager functionality
"""

import pytest
import pytest_asyncio
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from core.services.agent_manager import AgentManager, AgentState
from core.services.trust import TrustService
from core.services.audit import AuditService
from core.config import ZeroMeshConfig, SSLConfig, MCPConfig, TrustConfig, Mem0Config

@pytest_asyncio.fixture
async def mock_trust_service():
    """Create a mock trust service"""
    service = AsyncMock(spec=TrustService)
    service.initialized = True
    return service

@pytest_asyncio.fixture
async def mock_audit_service():
    """Create a mock audit service"""
    service = AsyncMock(spec=AuditService)
    service.initialized = True
    return service

@pytest_asyncio.fixture
async def agent_manager(tmp_path, mock_trust_service, mock_audit_service):
    """Create a test agent manager"""
    config = ZeroMeshConfig(
        ssl=SSLConfig(
            cert_path=str(tmp_path / "test.crt"),
            key_path=str(tmp_path / "test.key")
        ),
        mcp=MCPConfig(
            host="localhost",
            port=8000,
            api_key="test_key"
        ),
        trust=TrustConfig(
            score_threshold=0.7,
            decay_rate=0.1,
            quarantine_threshold=0.3
        ),
        mem0=Mem0Config(
            api_key="test_mem0_key"
        )
    )
    manager = AgentManager(config, mock_trust_service, mock_audit_service)
    await manager.initialize()
    return manager

@pytest.mark.asyncio
async def test_register_agent(agent_manager):
    """Test agent registration"""
    metadata = {"version": "1.0", "capabilities": ["test"]}
    success = await agent_manager.register_agent("test-agent", metadata)
    assert success

    state = agent_manager.get_agent_state("test-agent")
    assert state is not None
    assert state.status == "active"
    assert state.metadata == metadata
    assert isinstance(state.last_seen, datetime)

@pytest.mark.asyncio
async def test_block_agent(agent_manager):
    """Test agent blocking"""
    # First register the agent
    await agent_manager.register_agent("test-agent", {})

    # Then block it
    success = await agent_manager.block_agent("test-agent", "Suspicious activity")
    assert success

    state = agent_manager.get_agent_state("test-agent")
    assert state.status == "blocked"
    assert state.block_reason == "Suspicious activity"

    # Verify trust score was updated
    agent_manager.trust_service.update_trust_score.assert_called_once_with("test-agent", -1.0)

@pytest.mark.asyncio
async def test_quarantine_agent(agent_manager):
    """Test agent quarantine"""
    # First register the agent
    await agent_manager.register_agent("test-agent", {})

    # Then quarantine it
    success = await agent_manager.quarantine_agent("test-agent", "Trust score too low")
    assert success

    state = agent_manager.get_agent_state("test-agent")
    assert state.status == "quarantined"
    assert state.quarantine_reason == "Trust score too low"

@pytest.mark.asyncio
async def test_release_agent(agent_manager):
    """Test agent release"""
    # First register and block the agent
    await agent_manager.register_agent("test-agent", {})
    await agent_manager.block_agent("test-agent", "Test block")

    # Then release it
    success = await agent_manager.release_agent("test-agent")
    assert success

    state = agent_manager.get_agent_state("test-agent")
    assert state.status == "active"
    assert state.block_reason is None
    assert state.quarantine_reason is None

@pytest.mark.asyncio
async def test_update_agent_status(agent_manager):
    """Test agent status update"""
    # First register the agent
    await agent_manager.register_agent("test-agent", {})

    # Update status
    old_last_seen = agent_manager.get_agent_state("test-agent").last_seen
    await asyncio.sleep(0.1)  # Ensure time difference

    success = await agent_manager.update_agent_status("test-agent", "inactive")
    assert success

    state = agent_manager.get_agent_state("test-agent")
    assert state.status == "inactive"
    assert state.last_seen > old_last_seen

@pytest.mark.asyncio
async def test_unknown_agent_operations(agent_manager):
    """Test operations on unknown agents"""
    assert not await agent_manager.block_agent("unknown", "test")
    assert not await agent_manager.quarantine_agent("unknown", "test")
    assert not await agent_manager.release_agent("unknown")
    assert not await agent_manager.update_agent_status("unknown", "active")
    assert agent_manager.get_agent_state("unknown") is None

@pytest.mark.asyncio
async def test_cleanup(agent_manager):
    """Test agent manager cleanup"""
    await agent_manager.register_agent("test-agent", {})
    assert len(agent_manager.agents) > 0

    await agent_manager.cleanup()
    assert not agent_manager.initialized
    assert len(agent_manager.agents) == 0 