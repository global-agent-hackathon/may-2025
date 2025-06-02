"""
Base service class for ZeroMesh services
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional
from ..config import ZeroMeshConfig

logger = logging.getLogger(__name__)

class BaseService(ABC):
    """Base class for all services"""
    
    def __init__(self, config: ZeroMeshConfig):
        self.config = config
        self._initialized = False
        self._running = False
        
    @abstractmethod
    async def initialize(self):
        """Initialize the service"""
        pass
        
    async def start(self):
        """Start the service"""
        self._check_initialized()
        self._running = True
        
    async def stop(self):
        """Stop the service"""
        if self._running:
            self._running = False
            await self._cleanup()
        
    async def _cleanup(self):
        """Clean up resources - override in subclasses"""
        pass
        
    def _check_initialized(self):
        """Check if service is initialized"""
        if not self._initialized:
            raise RuntimeError(f"{self.__class__.__name__} not initialized")
            
    @property
    def initialized(self) -> bool:
        """Check if service is initialized"""
        return self._initialized
        
    @property
    def running(self) -> bool:
        """Check if service is running"""
        return self._running 