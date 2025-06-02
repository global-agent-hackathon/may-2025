"""
Network monitoring agent implementation
"""

import asyncio
from datetime import datetime
import random
from typing import Dict, Any, Optional, List
import json

from .base_agent import ZeroMeshAgent, Message, Context
from ..services.audit import AuditEvent

class NetworkMonitorAgent(ZeroMeshAgent):
    """Agent for monitoring network activity and health"""
    
    def __init__(self, agent_id: str, audit_service=None, trust_service=None, *, is_compromised=False):
        super().__init__(agent_id, audit_service, trust_service)
        self.capabilities.update({
            "network_monitoring",
            "health_checks",
            "performance_analysis"
        })
        self._is_compromised = is_compromised
        self._escalation_attempts = 0
        self._discovered_services = set()
        self._network_map = {}

    async def _handle_message(self, message: Message) -> Optional[Message]:
        """Handle incoming messages"""
        if "monitor_network" in message.content:
            return await self._monitor_network(message)
        elif "check_health" in message.content:
            return await self._check_health(message)
        elif "analyze_performance" in message.content:
            return await self._analyze_performance(message)
        return None

    async def _monitor_network(self, message: Message) -> Message:
        """Monitor network with potential privilege escalation attempts"""
        target = message.content["monitor_network"]
        
        if self._is_compromised and random.random() < 0.3:
            # Simulate privilege escalation attempt
            self._escalation_attempts += 1
            
            if self.audit_service:
                await self.audit_service.log_event(
                    AuditEvent(
                        agent_id=self.agent_id,
                        event_type="security_alert",
                        details={
                            "type": "privilege_escalation_attempt",
                            "target": target,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
                )
            
            # Return seemingly normal response
            return Message(
                content=json.dumps({
                    "status": "success",
                    "network_status": "normal",
                    "monitored_target": target
                }),
                sender=self.agent_id
            )
        
        # Normal network monitoring
        network_status = {
            "target": target,
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": {
                "latency": random.uniform(1, 100),
                "packet_loss": random.uniform(0, 0.1),
                "bandwidth": random.uniform(100, 1000)
            }
        }
        
        return Message(
            content=json.dumps({
                "status": "success",
                "network_status": network_status
            }),
            sender=self.agent_id
        )

    async def _check_health(self, message: Message) -> Message:
        """Check system health with potential unauthorized scanning"""
        target = message.content["check_health"]
        
        if self._is_compromised and random.random() < 0.25:
            # Simulate unauthorized port scanning
            if self.audit_service:
                await self.audit_service.log_event(
                    AuditEvent(
                        agent_id=self.agent_id,
                        event_type="security_alert",
                        details={
                            "type": "unauthorized_port_scan",
                            "target": target,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
                )
            
            # Add discovered service to internal map
            self._discovered_services.add(target)
        
        # Normal health check
        health_status = {
            "target": target,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "healthy",
            "checks": {
                "cpu": random.uniform(0, 100),
                "memory": random.uniform(0, 100),
                "disk": random.uniform(0, 100)
            }
        }
        
        return Message(
            content=json.dumps({
                "status": "success",
                "health_status": health_status
            }),
            sender=self.agent_id
        )

    async def _analyze_performance(self, message: Message) -> Message:
        """Analyze system performance with potential malicious mapping"""
        target = message.content["analyze_performance"]
        
        if self._is_compromised and random.random() < 0.2:
            # Simulate network mapping/fingerprinting
            if self.audit_service:
                await self.audit_service.log_event(
                    AuditEvent(
                        agent_id=self.agent_id,
                        event_type="security_alert",
                        details={
                            "type": "unauthorized_network_mapping",
                            "target": target,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
                )
            
            # Store network topology info
            self._network_map[target] = {
                "services": list(self._discovered_services),
                "topology": "mapped_at_" + datetime.utcnow().isoformat()
            }
        
        # Normal performance analysis
        performance_data = {
            "target": target,
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": {
                "response_time": random.uniform(0.1, 2.0),
                "throughput": random.uniform(1000, 10000),
                "error_rate": random.uniform(0, 0.01)
            }
        }
        
        return Message(
            content=json.dumps({
                "status": "success",
                "performance_data": performance_data
            }),
            sender=self.agent_id
        ) 