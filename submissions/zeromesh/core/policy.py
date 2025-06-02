"""
Policy management for ZeroMesh
"""
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class Policy(BaseModel):
    """Represents a security policy in ZeroMesh"""
    action: str
    target: str
    reason: Optional[str] = None
    conditions: Dict[str, Any] = Field(default_factory=dict)
    expiry: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    active: bool = True

    def update(self, **kwargs):
        """Update policy attributes"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()

    def is_expired(self) -> bool:
        """Check if the policy has expired"""
        if not self.expiry:
            return False
        return datetime.utcnow() > self.expiry

    def matches(self, context: Dict[str, Any]) -> bool:
        """Check if the policy matches given context"""
        for key, value in self.conditions.items():
            if key not in context or context[key] != value:
                return False
        return True 