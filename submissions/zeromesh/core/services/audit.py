"""
Audit service for logging agent activities
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import json
from pathlib import Path
from ..config import ZeroMeshConfig

logger = logging.getLogger(__name__)

class AuditEvent:
    """Represents an audit event"""
    def __init__(
        self,
        agent_id: str,
        event_type: str,
        details: Dict[str, Any],
        timestamp: Optional[datetime] = None
    ):
        self.event_type = event_type
        self.agent_id = agent_id
        self.details = details
        self.timestamp = timestamp or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary format"""
        return {
            "event_type": self.event_type,
            "agent_id": self.agent_id,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }

class AuditService:
    """Service for logging agent activities"""
    
    def __init__(self):
        self._registry = None
        self._initialized = False
        self._audit_logs = []
        
    async def initialize(self, registry):
        """Initialize the audit service"""
        if self._initialized:
            return
            
        self._registry = registry
        self._initialized = True
        
    async def cleanup(self):
        """Clean up resources"""
        self._initialized = False
        self._audit_logs.clear()
        
    async def log_event(self, event_type: str, data: Dict[str, Any]):
        """Log an audit event"""
        if not self._initialized:
            raise RuntimeError("Service not initialized")
            
        event = {
            "type": event_type,
            "timestamp": datetime.now(),
            "data": data
        }
        
        self._audit_logs.append(event)
        logger.info(f"Audit event logged: {event_type}")
        
    async def get_logs(
        self,
        event_type: str = None,
        start_time: datetime = None,
        end_time: datetime = None
    ) -> List[Dict[str, Any]]:
        """Query audit logs with filters"""
        if not self._initialized:
            raise RuntimeError("Service not initialized")
            
        filtered_logs = self._audit_logs
        
        if event_type:
            filtered_logs = [log for log in filtered_logs if log["type"] == event_type]
            
        if start_time:
            filtered_logs = [log for log in filtered_logs if log["timestamp"] >= start_time]
            
        if end_time:
            filtered_logs = [log for log in filtered_logs if log["timestamp"] <= end_time]
            
        return filtered_logs

    async def log_event(self, event: AuditEvent) -> bool:
        """Log an audit event to local storage"""
        if not self._initialized:
            raise RuntimeError("Audit service not initialized")

        event_dict = event.to_dict()
        self._audit_logs.append(event_dict)
        
        logger.info(f"Event logged: {event.event_type}")
        return True

    async def get_agent_events(self, agent_id: str, event_type: Optional[str] = None) -> list[Dict[str, Any]]:
        """Retrieve audit events for a specific agent from local storage"""
        if not self._initialized:
            raise RuntimeError("Audit service not initialized")

        events = [e for e in self._audit_logs if e["agent_id"] == agent_id]
        if event_type:
            events = [e for e in events if e["event_type"] == event_type]
        return events

    async def _flush_events(self):
        """Flush events to disk"""
        if not self._audit_logs:
            return
            
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"audit_{timestamp}.json"
        
        with open(log_file, 'w') as f:
            json.dump(self._audit_logs, f, indent=2)
            
        self._audit_logs.clear()
        logger.info(f"Flushed {len(self._audit_logs)} events to {log_file}")

    async def cleanup(self):
        """Clean up resources"""
        if self._audit_logs:
            await self._flush_events()
        self._initialized = False
        logger.info("Audit service cleaned up") 