"""
ZeroMesh Core Package

This package provides the core functionality for the ZeroMesh zero-trust agent communication system.
"""

from typing import Optional
import asyncio
import logging
from pathlib import Path

from .core import ZeroMesh
from .config import ZeroMeshConfig
from .aztp.protocol import AZTPConfig
from .policy.engine import PolicyEngine, Policy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instance
_instance: Optional[ZeroMesh] = None

async def initialize(
    cert_dir: str = "./certs",
    log_dir: str = "./logs",
    token_expiry: int = 3600,
    min_trust_score: float = 0.3
) -> ZeroMesh:
    """
    Initialize ZeroMesh with default configuration.
    
    Args:
        cert_dir: Directory for storing certificates
        log_dir: Directory for storing logs
        token_expiry: Token expiry time in seconds
        min_trust_score: Minimum trust score required for operations
        
    Returns:
        Initialized ZeroMesh instance
    """
    global _instance
    
    if _instance is not None:
        logger.warning("ZeroMesh already initialized")
        return _instance
        
    # Create necessary directories
    Path(cert_dir).mkdir(exist_ok=True)
    Path(log_dir).mkdir(exist_ok=True)
    
    # Create configuration
    config = ZeroMeshConfig(
        aztp_config=AZTPConfig(
            key_dir=cert_dir,
            token_expiry=token_expiry
        ),
        min_trust_score=min_trust_score,
        log_dir=log_dir
    )
    
    # Initialize ZeroMesh
    _instance = ZeroMesh()
    await _instance.initialize(config)
    
    return _instance

def get_instance() -> Optional[ZeroMesh]:
    """Get the global ZeroMesh instance if initialized"""
    return _instance

async def cleanup():
    """Clean up the global ZeroMesh instance"""
    global _instance
    
    if _instance is not None:
        await _instance.cleanup()
        _instance = None

# Export key classes for direct import
__all__ = [
    'ZeroMesh',
    'ZeroMeshConfig',
    'AZTPConfig',
    'PolicyEngine',
    'Policy',
    'initialize',
    'get_instance',
    'cleanup'
]

"""
Core services package for ZeroMesh
""" 