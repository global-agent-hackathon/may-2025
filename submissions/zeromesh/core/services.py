"""
Mock implementations of core services for the ZeroMesh dashboard
"""
from typing import Dict, Any
from datetime import datetime

class ServiceRegistry:
    def __init__(self):
        self._services = {}

    async def register_service(self, name: str, service_class):
        self._services[name] = service_class()

    async def initialize_all_services(self):
        for service in self._services.values():
            if hasattr(service, 'initialize'):
                await service.initialize()

    def get_service(self, name: str):
        return self._services.get(name)

    async def cleanup(self):
        for service in self._services.values():
            if hasattr(service, 'cleanup'):
                await service.cleanup()

class CoreService:
    async def initialize(self):
        pass

class AuthService:
    def __init__(self):
        self._agents = {
            "agent1": {"id": "agent1"},
            "agent2": {"id": "agent2"},
            "agent3": {"id": "agent3"}
        }

class TrustService:
    def __init__(self):
        self._trust_scores = {
            "agent1": 0.9,
            "agent2": 0.6,
            "agent3": 0.3
        }
        self._quarantined = {"agent3"}

    async def get_trust_score(self, agent_id: str) -> float:
        return self._trust_scores.get(agent_id, 0.0)

    def is_quarantined(self, agent_id: str) -> bool:
        return agent_id in self._quarantined

    async def update_trust_score(self, agent_id: str, score: float):
        self._trust_scores[agent_id] = score
        if score < 0.3:
            self._quarantined.add(agent_id)
        else:
            self._quarantined.discard(agent_id)

class AuditService:
    def __init__(self):
        self._logs = []

    async def get_logs(self, event_type=None, start_time=None, end_time=None):
        filtered_logs = self._logs
        
        if event_type:
            filtered_logs = [log for log in filtered_logs if log["type"] == event_type]
        
        if start_time:
            filtered_logs = [log for log in filtered_logs if datetime.fromisoformat(log["timestamp"]) >= start_time]
        
        if end_time:
            filtered_logs = [log for log in filtered_logs if datetime.fromisoformat(log["timestamp"]) <= end_time]
        
        return filtered_logs 