"""
Security demo script for ZeroMesh showing bad actor detection and response
"""

import asyncio
import logging
from datetime import datetime
import random
import json
import os
from pathlib import Path

from ..services.audit import AuditService, AuditEvent
from ..services.agent_manager import AgentManager
from ..services.trust import TrustService
from ..config import ZeroMeshConfig
from ..aztp.protocol import AZTPConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentSimulator:
    """Simulates agent behavior for demo purposes"""
    
    def __init__(self, agent_id: str, is_malicious: bool = False):
        self.agent_id = agent_id
        self.is_malicious = is_malicious
        self.blocked = False
        self.quarantined = False
        
        # Define possible actions
        self.normal_actions = [
            "data_sync",
            "heartbeat",
            "task_complete",
            "status_update"
        ]
        
        self.malicious_actions = [
            "unauthorized_access",
            "data_exfiltration",
            "system_exploit",
            "ddos_attempt",
            "privilege_escalation"
        ]

    async def perform_action(self, audit_service: AuditService, trust_service: TrustService) -> bool:
        """Perform a simulated action"""
        if self.blocked or self.quarantined:
            logger.warning(f"Agent {self.agent_id} is {self.blocked and 'blocked' or 'quarantined'}")
            return False

        if self.is_malicious and random.random() < 0.7:  # 70% chance of malicious action
            action = random.choice(self.malicious_actions)
            details = self._generate_malicious_details(action)
            trust_impact = -0.3  # Significant negative impact
        else:
            action = random.choice(self.normal_actions)
            details = self._generate_normal_details(action)
            trust_impact = 0.1  # Small positive impact

        # Log the action
        event = AuditEvent(
            action,
            self.agent_id,
            details
        )
        await audit_service.log_event(event)

        # Update trust score
        await trust_service.update_trust_score(self.agent_id, trust_impact)
        
        return True

    def _generate_normal_details(self, action: str) -> dict:
        """Generate details for normal actions"""
        base_details = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success"
        }
        
        if action == "data_sync":
            base_details.update({
                "bytes_synced": random.randint(1000, 10000),
                "files_processed": random.randint(1, 10)
            })
        elif action == "heartbeat":
            base_details.update({
                "uptime": random.randint(3600, 86400),
                "memory_usage": random.randint(100, 500)
            })
        elif action == "task_complete":
            base_details.update({
                "task_id": f"task_{random.randint(1000, 9999)}",
                "duration": random.randint(10, 300)
            })
        elif action == "status_update":
            base_details.update({
                "cpu_usage": random.randint(10, 90),
                "network_latency": random.randint(10, 100)
            })
            
        return base_details

    def _generate_malicious_details(self, action: str) -> dict:
        """Generate details for malicious actions"""
        base_details = {
            "timestamp": datetime.utcnow().isoformat(),
            "severity": "high",
            "detected_by": "security_monitor"
        }
        
        if action == "unauthorized_access":
            base_details.update({
                "target_resource": f"/secure/resource_{random.randint(1000, 9999)}",
                "attempt_count": random.randint(5, 20),
                "source_ip": f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
            })
        elif action == "data_exfiltration":
            base_details.update({
                "data_type": "sensitive",
                "bytes_transferred": random.randint(10000, 100000),
                "destination": f"malicious-domain-{random.randint(1, 100)}.com"
            })
        elif action == "system_exploit":
            base_details.update({
                "vulnerability": f"CVE-2024-{random.randint(1000, 9999)}",
                "exploit_type": "buffer_overflow",
                "target_system": "authentication_service"
            })
        elif action == "ddos_attempt":
            base_details.update({
                "requests_per_second": random.randint(1000, 10000),
                "target_endpoint": "/api/critical_service",
                "botnet_size": random.randint(50, 500)
            })
        elif action == "privilege_escalation":
            base_details.update({
                "target_privilege": "admin",
                "technique": "token_manipulation",
                "success": random.choice([True, False])
            })
            
        return base_details

async def run_security_demo():
    """Run the security demonstration"""
    # Create configuration
    config = ZeroMeshConfig(
        aztp_config=AZTPConfig(
            key_dir="./certs",
            token_expiry=3600,
            min_key_size=2048
        ),
        min_trust_score=0.3,  # This is our quarantine threshold
        max_trust_score=1.0,
        default_trust_score=0.5,
        trust_decay_rate=0.1,
        trust_update_interval=3600,
        log_dir="./logs",
        log_level="INFO"
    )

    # Initialize services
    audit_service = AuditService()
    audit_service.log_dir = Path(config.log_dir)  # Set log directory
    trust_service = TrustService()

    # Initialize basic services
    registry = {"config": config}
    await audit_service.initialize(registry)
    await trust_service.initialize(registry)

    # Initialize agent manager with dependencies
    agent_manager = AgentManager(config, trust_service, audit_service)
    await agent_manager.initialize()

    try:
        # Create agents
        agents = [
            AgentSimulator("good-agent-1"),
            AgentSimulator("good-agent-2"),
            AgentSimulator("malicious-agent-1", is_malicious=True),
            AgentSimulator("malicious-agent-2", is_malicious=True)
        ]

        # Register all agents
        for agent in agents:
            await agent_manager.register_agent(
                agent.agent_id,
                {"type": "demo_agent", "malicious": agent.is_malicious}
            )

        # Run simulation for 10 rounds
        for round_num in range(1, 11):
            logger.info(f"\n=== Round {round_num} ===")
            
            for agent in agents:
                if not agent.blocked and not agent.quarantined:
                    # Perform action and get trust score
                    await agent.perform_action(audit_service, trust_service)
                    trust_score = await trust_service.get_trust_score(agent.agent_id)
                    logger.info(f"Agent {agent.agent_id} trust score: {trust_score:.2f}")

                    # Check if agent should be quarantined
                    if trust_score < config.min_trust_score:  # Use min_trust_score instead of trust.quarantine_threshold
                        await agent_manager.quarantine_agent(
                            agent.agent_id,
                            f"Trust score too low: {trust_score:.2f}"
                        )
                        agent.quarantined = True

            # Sleep between rounds
            await asyncio.sleep(1)

    finally:
        # Clean up
        await audit_service.cleanup()
        await trust_service.cleanup()
        await agent_manager.cleanup()

if __name__ == "__main__":
    asyncio.run(run_security_demo()) 
