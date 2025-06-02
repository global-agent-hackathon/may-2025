"""
Service Registry for managing ZeroMesh services
"""

import logging
import importlib
from typing import Dict, Any, Type
from .base import BaseService
from ..config import ZeroMeshConfig

logger = logging.getLogger(__name__)

class ServiceRegistry:
    """Registry for managing services"""
    
    def __init__(self):
        self._services = {}
        self._config = None
        
    async def register_service(self, name: str, service_class: Type):
        """Register a service"""
        logger.info(f"Registered service {name} with class {service_class}")
        self._services[name] = {
            'class': service_class,
            'instance': None
        }
        
    async def initialize_service(self, name: str):
        """Initialize a registered service"""
        if name not in self._services:
            raise ValueError(f"Service {name} not registered")
            
        service_info = self._services[name]
        if service_info['instance'] is None:
            instance = service_info['class']()
            await instance.initialize(self)
            service_info['instance'] = instance
            
    async def initialize_all_services(self):
        """Initialize all registered services"""
        for name in self._services:
            await self.initialize_service(name)
            
    def get_service(self, name: str) -> Any:
        """Get a service instance"""
        if name not in self._services:
            raise ValueError(f"Service {name} not registered")
            
        service_info = self._services[name]
        if service_info['instance'] is None:
            raise RuntimeError(f"Service {name} not initialized")
            
        return service_info['instance']
        
    async def cleanup(self):
        """Clean up all services"""
        for service_info in self._services.values():
            if service_info['instance'] is not None:
                await service_info['instance'].cleanup()

    async def start_all(self):
        """Start all registered services"""
        for name, service in self._services.items():
            logger.info(f"Starting service: {name}")
            await service['instance'].start()

    async def stop_all(self):
        """Stop all registered services"""
        for name, service in self._services.items():
            logger.info(f"Stopping service: {name}")
            await service['instance'].stop() 