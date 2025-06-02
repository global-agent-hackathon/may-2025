"""
ZeroMesh configuration
"""
from typing import Optional
from pydantic import BaseModel
from .aztp.protocol import AZTPConfig

class ZeroMeshConfig(BaseModel):
    """Configuration for ZeroMesh"""
    aztp_config: AZTPConfig
    min_trust_score: float = 0.3
    max_trust_score: float = 1.0
    default_trust_score: float = 0.5
    trust_decay_rate: float = 0.1  # How quickly trust decays over time
    trust_update_interval: int = 3600  # How often to update trust scores (in seconds)
    
    # Logging configuration
    log_dir: str = "./logs"
    log_level: str = "INFO"
    
    # Policy configuration
    default_policy_priority: int = 0
    policy_cache_ttl: int = 300  # How long to cache policy decisions (in seconds)
    
    # Audit configuration
    audit_retention_days: int = 30
    audit_batch_size: int = 100
    
    # System configuration
    cleanup_interval: int = 3600  # How often to run cleanup tasks (in seconds)
    max_agents: int = 1000  # Maximum number of agents allowed
    
    class Config:
        arbitrary_types_allowed = True  # Allow AZTPConfig type 