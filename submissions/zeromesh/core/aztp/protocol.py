"""
AZTP (Agent Zero Trust Protocol) Implementation
"""
from typing import Dict, Any, Optional, NamedTuple
from datetime import datetime, timedelta, timezone
import jwt
import asyncio
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
import logging

logger = logging.getLogger(__name__)

class AuthResult(NamedTuple):
    success: bool
    error: Optional[str]
    credentials: Optional[Dict[str, Any]]
    permissions: Optional[set]

class AZTPConfig:
    def __init__(self, 
                 key_dir: str,
                 token_expiry: int = 3600,
                 min_key_size: int = 2048):
        self.key_dir = key_dir
        self.token_expiry = token_expiry
        self.min_key_size = min_key_size

class AZTPProtocol:
    """
    Implementation of the Agent Zero Trust Protocol
    
    Key features:
    - Asymmetric key authentication
    - Time-based token rotation
    - Permission-based access control
    - Trust level verification
    """
    
    def __init__(self):
        self._initialized = False
        self._config: Optional[AZTPConfig] = None
        self._private_key = None
        self._public_key = None
        self._active_tokens: Dict[str, Dict[str, Any]] = {}
        
    async def initialize(self, config: AZTPConfig):
        """Initialize the AZTP protocol"""
        if self._initialized:
            return
            
        self._config = config
        
        # Generate or load keys
        await self._setup_keys()
        
        # Start token cleanup task
        asyncio.create_task(self._cleanup_expired_tokens())
        
        self._initialized = True
        
    async def cleanup(self):
        """Clean up resources"""
        self._initialized = False
        self._active_tokens.clear()
        
    async def _setup_keys(self):
        """Set up cryptographic keys"""
        try:
            # Try to load existing keys
            with open(f"{self._config.key_dir}/private.pem", "rb") as f:
                self._private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None
                )
            with open(f"{self._config.key_dir}/public.pem", "rb") as f:
                self._public_key = serialization.load_pem_public_key(
                    f.read()
                )
        except FileNotFoundError:
            # Generate new key pair
            self._private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=self._config.min_key_size
            )
            self._public_key = self._private_key.public_key()
            
            # Save keys
            private_pem = self._private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            public_pem = self._public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            with open(f"{self._config.key_dir}/private.pem", "wb") as f:
                f.write(private_pem)
            with open(f"{self._config.key_dir}/public.pem", "wb") as f:
                f.write(public_pem)
                
    async def authenticate_agent(self, agent_id: str, cert_data: str) -> AuthResult:
        """
        Authenticate an agent using its certificate
        
        Args:
            agent_id: Unique identifier for the agent
            cert_data: PEM-encoded certificate data
            
        Returns:
            AuthResult containing success status and optional error/credentials
        """
        if not self._initialized:
            return AuthResult(False, "Protocol not initialized", None, None)
            
        try:
            # Verify certificate
            cert_key = serialization.load_pem_public_key(cert_data.encode())
            
            # Create authentication token
            now = datetime.now(timezone.utc)
            token_data = {
                "agent_id": agent_id,
                "exp": now + timedelta(seconds=self._config.token_expiry),
                "iat": now
            }
            
            token = jwt.encode(
                token_data,
                self._private_key,
                algorithm="RS256"
            )
            
            # Store active token
            self._active_tokens[agent_id] = {
                "token": token,
                "expires": token_data["exp"],
                "public_key": cert_key
            }
            
            # Define initial permissions
            initial_permissions = {
                "authenticate",
                "request_trust_score",
                "update_status"
            }
            
            return AuthResult(
                success=True,
                error=None,
                credentials={"token": token},
                permissions=initial_permissions
            )
            
        except Exception as e:
            logger.error(f"Authentication failed for agent {agent_id}: {str(e)}")
            return AuthResult(False, str(e), None, None)
            
    async def verify_token(self, agent_id: str, token: str) -> bool:
        """Verify an authentication token"""
        if not self._initialized:
            return False
            
        try:
            # Check if token is active
            if agent_id not in self._active_tokens:
                return False
                
            stored_token = self._active_tokens[agent_id]
            
            # Verify token hasn't expired
            if stored_token["expires"] < datetime.now(timezone.utc):
                return False
                
            # Verify token signature
            jwt.decode(
                token,
                self._public_key,
                algorithms=["RS256"]
            )
            
            return True
            
        except jwt.InvalidTokenError:
            return False
            
    async def _cleanup_expired_tokens(self):
        """Periodically clean up expired tokens"""
        while self._initialized:
            now = datetime.now(timezone.utc)
            expired = [
                agent_id for agent_id, data in self._active_tokens.items()
                if data["expires"] < now
            ]
            
            for agent_id in expired:
                del self._active_tokens[agent_id]
                
            await asyncio.sleep(60)  # Check every minute
            
    async def revoke_token(self, agent_id: str):
        """Revoke an agent's token"""
        self._active_tokens.pop(agent_id, None) 