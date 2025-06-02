"""
ZeroMesh initialization script
"""
import asyncio
import logging
from core.services import (
    ServiceRegistry,
    CoreService,
    AuthService,
    TrustService,
    AuditService
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Main initialization function"""
    print("Initializing ZeroMesh...")
    
    # Create service registry
    registry = ServiceRegistry()
    
    # Register services
    await registry.register_service("core", CoreService)
    await registry.register_service("auth", AuthService)
    await registry.register_service("trust", TrustService)
    await registry.register_service("audit", AuditService)
    
    # Initialize all services
    await registry.initialize_all_services()
    
    print("\nRegistering test agents...")
    
    # Get core service
    core_service = registry.get_service("core")
    
    # Register test agents
    test_agents = [
        ("agent1", {"token": "test_token_1"}),
        ("agent2", {"token": "test_token_2"}),
        ("agent3", {"token": "test_token_3"})
    ]
    
    auth_service = registry.get_service("auth")
    for agent_id, credentials in test_agents:
        await auth_service.register_agent(agent_id, credentials)
        logger.info(f"Registered agent: {agent_id}")
    
    print("\nCleaning up...")
    await registry.cleanup()
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main()) 