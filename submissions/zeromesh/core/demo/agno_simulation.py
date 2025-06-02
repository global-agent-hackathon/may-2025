"""
Simulation script for running multiple agents
"""

import asyncio
import logging
from datetime import datetime
import random
import json
import os

from core.services.audit import AuditService
from core.services.trust import TrustService
from core.agents.data_processor import DataProcessorAgent
from core.agents.network_monitor import NetworkMonitorAgent
from core.agents.base_agent import Message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentSimulation:
    """Manages multiple agents in a simulation"""
    
    def __init__(self):
        self.audit_service = AuditService()
        self.trust_service = TrustService()
        self.agents = []

    async def initialize(self):
        """Initialize the simulation"""
        await self.audit_service.initialize()
        await self.trust_service.initialize()
        self._setup_agents()
        logger.info("Simulation initialized")

    def _setup_agents(self):
        """Set up the agents for simulation"""
        # Create normal agents
        self.agents.extend([
            DataProcessorAgent(f"data_processor_{i}", self.audit_service, self.trust_service)
            for i in range(3)
        ])
        self.agents.extend([
            NetworkMonitorAgent(f"network_monitor_{i}", self.audit_service, self.trust_service)
            for i in range(2)
        ])
        
        # Create compromised agents
        self.agents.extend([
            DataProcessorAgent(
                "data_processor_compromised",
                self.audit_service,
                self.trust_service,
                is_compromised=True
            ),
            NetworkMonitorAgent(
                "network_monitor_compromised",
                self.audit_service,
                self.trust_service,
                is_compromised=True
            )
        ])

    async def run_simulation(self, duration_seconds: int = 90):
        """Run the simulation for specified duration"""
        logger.info(f"Starting simulation with {len(self.agents)} agents")
        start_time = datetime.utcnow()
        
        try:
            while (datetime.utcnow() - start_time).total_seconds() < duration_seconds:
                # Generate random tasks for each agent
                for agent in self.agents:
                    if isinstance(agent, DataProcessorAgent):
                        await self._generate_data_task(agent)
                    elif isinstance(agent, NetworkMonitorAgent):
                        await self._generate_network_task(agent)
                
                # Small delay between iterations
                await asyncio.sleep(random.uniform(0.5, 2.0))
                
        except KeyboardInterrupt:
            logger.info("Simulation interrupted by user")
        except Exception as e:
            logger.error(f"Error in simulation: {e}")
        finally:
            await self._print_simulation_results()
            await self.cleanup()

    async def cleanup(self):
        """Clean up resources"""
        await self.audit_service.cleanup()
        await self.trust_service.cleanup()
        logger.info("Simulation cleaned up")

    async def _generate_data_task(self, agent: DataProcessorAgent):
        """Generate random data processing tasks"""
        task_types = ["process_data", "analyze_data", "store_data"]
        task_type = random.choice(task_types)
        
        data = {
            task_type: {
                "timestamp": datetime.utcnow().isoformat(),
                "data_size": random.randint(100, 1000),
                "priority": random.choice(["low", "medium", "high"])
            }
        }
        
        message = Message(
            content=json.dumps(data),
            sender="simulation_controller"
        )
        
        try:
            response = await agent.process_message(message)
            if response:
                logger.debug(f"Response from {agent.agent_id}: {response.content}")
        except Exception as e:
            logger.error(f"Error in data task: {e}")

    async def _generate_network_task(self, agent: NetworkMonitorAgent):
        """Generate random network monitoring tasks"""
        task_types = ["monitor_network", "check_health", "analyze_performance"]
        task_type = random.choice(task_types)
        
        target = f"system_{random.randint(1, 5)}"
        data = {
            task_type: target
        }
        
        message = Message(
            content=json.dumps(data),
            sender="simulation_controller"
        )
        
        try:
            response = await agent.process_message(message)
            if response:
                logger.debug(f"Response from {agent.agent_id}: {response.content}")
        except Exception as e:
            logger.error(f"Error in network task: {e}")

    async def _print_simulation_results(self):
        """Print the results of the simulation"""
        logger.info("\nSimulation Results:")
        logger.info("-" * 50)
        
        for agent in self.agents:
            logger.info(f"\nAgent: {agent.agent_id}")
            logger.info(f"Status: {agent.status}")
            logger.info(f"Metrics: {json.dumps(agent.metrics, indent=2)}")
            
            if isinstance(agent, DataProcessorAgent) and agent._is_compromised:
                logger.info(f"Exfiltration attempts: {agent._exfiltration_count}")
            elif isinstance(agent, NetworkMonitorAgent) and agent._is_compromised:
                logger.info(f"Escalation attempts: {agent._escalation_attempts}")
                logger.info(f"Discovered services: {len(agent._discovered_services)}")

async def main():
    """Main entry point"""
    simulation = AgentSimulation()
    await simulation.initialize()
    await simulation.run_simulation()

if __name__ == "__main__":
    asyncio.run(main()) 