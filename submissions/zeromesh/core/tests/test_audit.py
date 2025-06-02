"""
Tests for audit service functionality
"""

import pytest
import pytest_asyncio
from datetime import datetime
import json
from unittest.mock import AsyncMock, MagicMock, patch

from core.services.audit import AuditService, AuditEvent
from core.config import ZeroMeshConfig, SSLConfig, MCPConfig, TrustConfig, Mem0Config

class MockResponse:
    def __init__(self, status, data=None):
        self.status = status
        self._data = data

    async def json(self):
        return self._data

    async def text(self):
        return json.dumps(self._data) if self._data else ""

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

@pytest_asyncio.fixture
async def mock_session():
    """Create a mock aiohttp session"""
    session = AsyncMock()
    session.post = AsyncMock()
    return session

@pytest_asyncio.fixture
async def audit_service(tmp_path, mock_session):
    """Create a test audit service"""
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
    
    with patch('aiohttp.ClientSession', return_value=mock_session):
        service = AuditService(config)
        await service.initialize()
        return service

@pytest.mark.asyncio
async def test_audit_event_creation():
    """Test audit event creation"""
    event = AuditEvent(
        "test_event",
        "test-agent",
        {"action": "test"}
    )
    assert event.event_type == "test_event"
    assert event.agent_id == "test-agent"
    assert event.details == {"action": "test"}
    assert isinstance(event.timestamp, datetime)

@pytest.mark.asyncio
async def test_audit_event_to_dict():
    """Test audit event serialization"""
    event = AuditEvent(
        "test_event",
        "test-agent",
        {"action": "test"},
        timestamp=datetime(2025, 1, 1, 12, 0)
    )
    event_dict = event.to_dict()
    assert event_dict["event_type"] == "test_event"
    assert event_dict["agent_id"] == "test-agent"
    assert event_dict["details"] == {"action": "test"}
    assert event_dict["timestamp"] == "2025-01-01T12:00:00"

@pytest.mark.asyncio
async def test_audit_log_event(audit_service, mock_session):
    """Test logging an audit event"""
    # Setup mock response
    mock_session.post.return_value = MockResponse(201)

    event = AuditEvent(
        "test_event",
        "test-agent",
        {"action": "test"}
    )
    success = await audit_service.log_event(event)
    assert success

    # Verify correct API call
    mock_session.post.assert_called_once()
    args = mock_session.post.call_args
    assert args[0][0].endswith("/memories")
    assert "content" in args[1]["json"]
    assert "metadata" in args[1]["json"]

@pytest.mark.asyncio
async def test_audit_get_events(audit_service, mock_session):
    """Test retrieving audit events"""
    # Setup mock responses
    mock_session.post.side_effect = [
        # Log event responses
        MockResponse(201),
        MockResponse(201),
        MockResponse(201),
        # Get events response
        MockResponse(200, [
            {
                "content": json.dumps({
                    "event_type": "event1",
                    "agent_id": "agent1",
                    "details": {"action": "test1"},
                    "timestamp": "2025-01-01T12:00:00"
                })
            },
            {
                "content": json.dumps({
                    "event_type": "event2",
                    "agent_id": "agent1",
                    "details": {"action": "test2"},
                    "timestamp": "2025-01-01T12:00:00"
                })
            }
        ])
    ]

    # Log test events
    events = [
        AuditEvent("event1", "agent1", {"action": "test1"}),
        AuditEvent("event2", "agent1", {"action": "test2"}),
        AuditEvent("event1", "agent2", {"action": "test3"})
    ]
    for event in events:
        await audit_service.log_event(event)

    # Test filtering by agent
    agent1_events = await audit_service.get_agent_events("agent1")
    assert len(agent1_events) == 2
    assert all(e["agent_id"] == "agent1" for e in agent1_events)

@pytest.mark.asyncio
async def test_audit_cleanup(audit_service):
    """Test audit service cleanup"""
    assert audit_service.initialized
    await audit_service.cleanup()
    assert not audit_service.initialized 