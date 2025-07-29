"""Basic tests for the agent team setup."""

import pytest
import os
from agents.main import create_agent_team
from config import settings

# Skip tests if the API key is not available, as team creation might fail
pytestmark = pytest.mark.skipif(not settings.OPENROUTER_API_KEY, reason="OPENROUTER_API_KEY not set in environment")

def test_create_agent_team():
    """Test if the agent team can be created without errors."""
    try:
        team = create_agent_team()
        assert team is not None
        assert team.coordinator is not None
        assert len(team.members) > 0
        print(f"\nSuccessfully created team with coordinator '{team.coordinator.name}' and {len(team.members)} members.")
    except Exception as e:
        pytest.fail(f"Failed to create agent team: {e}")

# You could add more tests here, e.g.:
# - Test individual agent instantiation
# - Test coordinator trigger logic (if made testable)
# - Test team invocation with mock input (might require more setup) 