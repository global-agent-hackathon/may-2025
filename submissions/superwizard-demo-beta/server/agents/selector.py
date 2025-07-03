# Agent selector utilities
from typing import Optional
from .superwizard_agent import get_superwizard_agent

def get_agent(agent_type: str = "superwizard", **kwargs):
    """Get an agent instance based on type"""
    if agent_type == "superwizard":
        return get_superwizard_agent(**kwargs)
    else:
        raise ValueError(f"Unknown agent type: {agent_type}") 