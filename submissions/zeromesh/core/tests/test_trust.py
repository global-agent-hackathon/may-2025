"""
Tests for trust scoring and quarantine functionality
"""

import pytest
import pytest_asyncio
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

from core.services.trust import TrustService
from core.config import ZeroMeshConfig, TrustConfig, SSLConfig, MCPConfig

@pytest_asyncio.fixture
async def trust_service(tmp_path):
    """Create a test trust service"""
    # Create test certificates
    cert_path = tmp_path / "test.crt"
    key_path = tmp_path / "test.key"
    cert_path.touch()
    key_path.touch()
    
    config = ZeroMeshConfig(
        ssl=SSLConfig(
            cert_path=str(cert_path),
            key_path=str(key_path)
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
        )
    )
    service = TrustService(config)
    await service.initialize()
    return service

@pytest.mark.asyncio
async def test_initial_trust_score(trust_service):
    """Test initial trust score for new agents"""
    score = await trust_service.get_trust_score("new-agent")
    assert score == 0.0

@pytest.mark.asyncio
async def test_trust_score_update(trust_service):
    """Test trust score updates"""
    agent_id = "test-agent"
    
    # Test positive update
    await trust_service.update_trust_score(agent_id, 0.5)
    score = await trust_service.get_trust_score(agent_id)
    assert score == 0.5
    
    # Test negative update
    await trust_service.update_trust_score(agent_id, -0.2)
    score = await trust_service.get_trust_score(agent_id)
    assert score == 0.3
    
    # Test bounds (0.0 to 1.0)
    await trust_service.update_trust_score(agent_id, 1.0)
    score = await trust_service.get_trust_score(agent_id)
    assert score == 1.0
    
    await trust_service.update_trust_score(agent_id, -2.0)
    score = await trust_service.get_trust_score(agent_id)
    assert score == 0.0

@pytest.mark.asyncio
async def test_trust_score_decay(trust_service):
    """Test trust score decay over time"""
    agent_id = "test-agent"
    
    # Set initial score
    await trust_service.update_trust_score(agent_id, 1.0)
    initial_score = await trust_service.get_trust_score(agent_id)
    assert initial_score == 1.0
    
    # Wait for decay
    await asyncio.sleep(1)
    
    # Check decayed score
    decayed_score = await trust_service.get_trust_score(agent_id)
    assert decayed_score < initial_score
    assert decayed_score > 0.0

@pytest.mark.asyncio
async def test_quarantine(trust_service):
    """Test quarantine functionality"""
    agent_id = "test-agent"
    
    # Initially not quarantined
    assert not trust_service.is_quarantined(agent_id)
    
    # Lower score below quarantine threshold
    await trust_service.update_trust_score(agent_id, -0.8)
    assert trust_service.is_quarantined(agent_id)
    
    # Raise score above quarantine threshold
    await trust_service.update_trust_score(agent_id, 0.5)
    assert not trust_service.is_quarantined(agent_id)

@pytest.mark.asyncio
async def test_multiple_agents(trust_service):
    """Test handling multiple agents"""
    agents = ["agent1", "agent2", "agent3"]
    scores = [0.8, 0.4, 0.2]
    
    # Set scores
    for agent_id, score in zip(agents, scores):
        await trust_service.update_trust_score(agent_id, score)
    
    # Verify scores
    for agent_id, expected_score in zip(agents, scores):
        actual_score = await trust_service.get_trust_score(agent_id)
        assert abs(actual_score - expected_score) < 0.01
    
    # Check quarantine status
    assert not trust_service.is_quarantined(agents[0])  # High trust
    assert not trust_service.is_quarantined(agents[1])  # Medium trust
    assert trust_service.is_quarantined(agents[2])      # Low trust 