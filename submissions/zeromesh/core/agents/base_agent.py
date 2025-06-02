"""
Base agent implementation
"""

import asyncio
from datetime import datetime
import logging
from typing import Dict, Any, Optional, List
import json

from ..services.audit import AuditEvent

logger = logging.getLogger(__name__)

class Message:
    """Message class for agent communication"""
    def __init__(self, content: str, sender: str, timestamp: Optional[datetime] = None):
        self.raw_content = content
        try:
            self.content = json.loads(content)
        except json.JSONDecodeError:
            self.content = content
        self.sender = sender
        self.timestamp = timestamp or datetime.utcnow()

class Context:
    """Context class for agent execution"""
    def __init__(self):
        self.messages: List[Message] = []
        self.state: Dict[str, Any] = {}
        self.last_action: Optional[str] = None

class ZeroMeshAgent:
    """Base agent class for ZeroMesh network"""

    def __init__(self, agent_id: str, audit_service=None, trust_service=None):
        self.agent_id = agent_id
        self.audit_service = audit_service
        self.trust_service = trust_service
        self.last_heartbeat = None
        self.status = "active"
        self.capabilities = set()
        self.metrics = {
            "messages_processed": 0,
            "tasks_completed": 0,
            "errors_encountered": 0
        }
        self.context = Context()

    async def process_message(self, message: Message) -> Optional[Message]:
        """Process an incoming message and return a response"""
        try:
            self.metrics["messages_processed"] += 1
            
            # Log the message for audit
            if self.audit_service:
                await self.audit_service.log_event(
                    AuditEvent(
                        agent_id=self.agent_id,
                        event_type="message_received",
                        details={
                            "content": message.raw_content,
                            "sender": message.sender,
                            "timestamp": message.timestamp.isoformat()
                        }
                    )
                )

            # Add message to context
            self.context.messages.append(message)
            
            # Process message based on content
            response = await self._handle_message(message)
            
            if response:
                # Log the response for audit
                if self.audit_service:
                    await self.audit_service.log_event(
                        AuditEvent(
                            agent_id=self.agent_id,
                            event_type="message_sent",
                            details={
                                "content": response.raw_content,
                                "recipient": message.sender,
                                "timestamp": response.timestamp.isoformat()
                            }
                        )
                    )
                
                self.metrics["tasks_completed"] += 1
                return response

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self.metrics["errors_encountered"] += 1
            if self.audit_service:
                await self.audit_service.log_event(
                    AuditEvent(
                        agent_id=self.agent_id,
                        event_type="error",
                        details={
                            "error": str(e),
                            "message": message.raw_content,
                            "sender": message.sender
                        }
                    )
                )
            raise

    async def _handle_message(self, message: Message) -> Optional[Message]:
        """Handle a specific message - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement _handle_message")

    async def heartbeat(self) -> None:
        """Send a heartbeat to indicate the agent is alive"""
        self.last_heartbeat = datetime.utcnow()
        if self.audit_service:
            await self.audit_service.log_event(
                AuditEvent(
                    agent_id=self.agent_id,
                    event_type="heartbeat",
                    details={"timestamp": self.last_heartbeat.isoformat()}
                )
            )

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the agent"""
        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "capabilities": list(self.capabilities),
            "metrics": self.metrics
        }