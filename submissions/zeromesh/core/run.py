"""
Main entry point for running the ZeroMesh service
"""

import asyncio
import logging
from .config import load_config
from .services.registry import ServiceRegistry
from .services.core import CoreService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main entry point for ZeroMesh"""
    # Load configuration
    config = load_config()

    # Create service registry
    registry = ServiceRegistry(config)

    # Register services
    registry.register_service_type("core", CoreService)
    # Register other services here as they are implemented

    try:
        # Initialize core service
        await registry.initialize_service("core")

        # Start all services
        await registry.start_all()
        logger.info("ZeroMesh services started successfully")

        # Keep the service running
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info("Shutting down ZeroMesh services...")
    except Exception as e:
        logger.error(f"Error running ZeroMesh services: {e}")
    finally:
        await registry.stop_all()
        logger.info("ZeroMesh services stopped") 