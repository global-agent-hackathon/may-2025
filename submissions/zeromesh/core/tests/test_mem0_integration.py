"""
Test script for verifying Mem0 integration
"""

import asyncio
import os
from datetime import datetime
import logging
import json

from zeromesh.services.audit import AuditService, AuditEvent
from zeromesh.config import ZeroMeshConfig, SSLConfig, MCPConfig, TrustConfig, Mem0Config, AuditConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_mem0_integration():
    """Test Mem0 integration with real API calls"""
    # Get Mem0 API key from environment
    mem0_api_key = os.getenv("MEM0_API_KEY")
    if not mem0_api_key:
        logger.error("MEM0_API_KEY environment variable not set")
        return False

    # Create configuration
    config = ZeroMeshConfig(
        ssl=SSLConfig(
            cert_path="certs/test.crt",
            key_path="certs/test.key"
        ),
        mcp=MCPConfig(
            host="localhost",
            port=8000,
            api_key="test"
        ),
        trust=TrustConfig(
            score_threshold=0.7,
            decay_rate=0.1,
            quarantine_threshold=0.3
        ),
        audit=AuditConfig(
            log_dir="logs",
            batch_size=100,
            flush_interval=60
        ),
        mem0=Mem0Config(
            api_key=mem0_api_key
        )
    )

    # Create audit service
    audit_service = AuditService(config)
    await audit_service.initialize()

    try:
        # Test 1: Log a simple event
        logger.info("\nTest 1: Logging simple event...")
        test_event = AuditEvent(
            "test_integration",
            "test-agent-1",
            {
                "action": "integration_test",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        success = await audit_service.log_event(test_event)
        if not success:
            logger.error("Failed to log simple event")
            return False
        logger.info("✓ Simple event logged successfully")

        # Test 2: Log an event with complex details
        logger.info("\nTest 2: Logging event with complex details...")
        complex_event = AuditEvent(
            "security_alert",
            "test-agent-1",
            {
                "alert_type": "unauthorized_access",
                "severity": "high",
                "source_ip": "192.168.1.100",
                "attempted_action": "system_access",
                "blocked": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        success = await audit_service.log_event(complex_event)
        if not success:
            logger.error("Failed to log complex event")
            return False
        logger.info("✓ Complex event logged successfully")

        # Test 3: Log events for a different agent
        logger.info("\nTest 3: Logging events for different agent...")
        other_event = AuditEvent(
            "connection_status",
            "test-agent-2",
            {
                "status": "connected",
                "uptime": 3600,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        success = await audit_service.log_event(other_event)
        if not success:
            logger.error("Failed to log event for different agent")
            return False
        logger.info("✓ Event logged successfully for different agent")

        # Test 4: Retrieve events for first agent
        logger.info("\nTest 4: Retrieving events for first agent...")
        events = await audit_service.get_agent_events("test-agent-1")
        
        if not events:
            logger.warning("No events retrieved for first agent")
        else:
            logger.info(f"✓ Retrieved {len(events)} events for first agent:")
            for event in events:
                logger.info(f"  - Type: {event['event_type']}")
                logger.info(f"    Details: {json.dumps(event['details'], indent=2)}")

        # Test 5: Filter events by type
        logger.info("\nTest 5: Filtering events by type...")
        security_events = await audit_service.get_agent_events("test-agent-1", "security_alert")
        
        if not security_events:
            logger.warning("No security events found")
        else:
            logger.info(f"✓ Found {len(security_events)} security events:")
            for event in security_events:
                logger.info(f"  - Details: {json.dumps(event['details'], indent=2)}")

        # Test 6: Verify events for second agent
        logger.info("\nTest 6: Verifying events for second agent...")
        other_events = await audit_service.get_agent_events("test-agent-2")
        
        if not other_events:
            logger.warning("No events found for second agent")
        else:
            logger.info(f"✓ Found {len(other_events)} events for second agent:")
            for event in other_events:
                logger.info(f"  - Type: {event['event_type']}")
                logger.info(f"    Details: {json.dumps(event['details'], indent=2)}")

        return True

    except Exception as e:
        logger.error(f"Error during Mem0 integration test: {e}")
        return False

    finally:
        await audit_service.cleanup()

if __name__ == "__main__":
    asyncio.run(test_mem0_integration()) 