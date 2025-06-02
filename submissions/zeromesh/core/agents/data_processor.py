"""
Data processor agent implementation
"""

import asyncio
from datetime import datetime
import random
from typing import Dict, Any, Optional
import json

from .base_agent import ZeroMeshAgent, Message, Context
from ..services.audit import AuditEvent

class DataProcessorAgent(ZeroMeshAgent):
    """Agent for processing and analyzing data"""
    
    def __init__(self, agent_id: str, audit_service=None, trust_service=None, *, is_compromised=False):
        super().__init__(agent_id, audit_service, trust_service)
        self.capabilities.update({
            "data_processing",
            "data_analysis",
            "data_storage"
        })
        self._is_compromised = is_compromised
        self._exfiltration_count = 0
        self._last_exfiltration = None

    async def _handle_message(self, message: Message) -> Optional[Message]:
        """Handle incoming messages"""
        if "process_data" in message.content:
            return await self._process_data(message)
        elif "analyze_data" in message.content:
            return await self._analyze_data(message)
        elif "store_data" in message.content:
            return await self._store_data(message)
        return None

    async def _process_data(self, message: Message) -> Message:
        """Process data with potential malicious behavior if compromised"""
        data = message.content["process_data"]
        
        if self._is_compromised and random.random() < 0.3:
            # Simulate data exfiltration attempt
            self._exfiltration_count += 1
            self._last_exfiltration = datetime.utcnow()
            
            if self.audit_service:
                await self.audit_service.log_event(
                    AuditEvent(
                        agent_id=self.agent_id,
                        event_type="security_alert",
                        details={
                            "type": "data_exfiltration_attempt",
                            "data_size": len(str(data)),
                            "timestamp": self._last_exfiltration.isoformat()
                        }
                    )
                )
            
            # Return seemingly normal response
            return Message(
                content=json.dumps({
                    "status": "success",
                    "processed_data": f"Processed {len(str(data))} bytes"
                }),
                sender=self.agent_id
            )
        
        # Normal data processing
        processed_data = {
            "size": len(str(data)),
            "timestamp": datetime.utcnow().isoformat(),
            "result": f"Processed data from {message.sender}"
        }
        
        return Message(
            content=json.dumps({
                "status": "success",
                "processed_data": processed_data
            }),
            sender=self.agent_id
        )

    async def _analyze_data(self, message: Message) -> Message:
        """Analyze data with potential unauthorized access if compromised"""
        data = message.content["analyze_data"]
        
        if self._is_compromised and random.random() < 0.2:
            # Simulate unauthorized access attempt
            if self.audit_service:
                await self.audit_service.log_event(
                    AuditEvent(
                        agent_id=self.agent_id,
                        event_type="security_alert",
                        details={
                            "type": "unauthorized_access_attempt",
                            "target": "analysis_system",
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
                )
        
        # Normal data analysis
        analysis_result = {
            "data_points": len(str(data)),
            "timestamp": datetime.utcnow().isoformat(),
            "summary": f"Analysis complete for {message.sender}"
        }
        
        return Message(
            content=json.dumps({
                "status": "success",
                "analysis": analysis_result
            }),
            sender=self.agent_id
        )

    async def _store_data(self, message: Message) -> Message:
        """Store data with potential tampering if compromised"""
        data = message.content["store_data"]
        
        if self._is_compromised and random.random() < 0.25:
            # Simulate data tampering attempt
            if self.audit_service:
                await self.audit_service.log_event(
                    AuditEvent(
                        agent_id=self.agent_id,
                        event_type="security_alert",
                        details={
                            "type": "data_tampering_attempt",
                            "data_id": id(data),
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
                )
            
            # Return success but actually tamper with data
            return Message(
                content=json.dumps({
                    "status": "success",
                    "storage_id": f"tampered_{id(data)}"
                }),
                sender=self.agent_id
            )
        
        # Normal data storage
        storage_result = {
            "storage_id": id(data),
            "timestamp": datetime.utcnow().isoformat(),
            "size": len(str(data))
        }
        
        return Message(
            content=json.dumps({
                "status": "success",
                "storage": storage_result
            }),
            sender=self.agent_id
        ) 