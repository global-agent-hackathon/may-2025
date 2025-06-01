import os
import jwt
import requests
import base64
from typing import Optional, Dict, Any
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

# Security scheme for Bearer token
security = HTTPBearer()

class ClerkAuth:
    def __init__(self):
        self.clerk_secret_key = os.getenv("CLERK_SECRET_KEY")
        self.clerk_publishable_key = os.getenv("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY")
        
        if not self.clerk_secret_key:
            logger.warning("CLERK_SECRET_KEY not found. Authentication will be disabled.")
        
        # Extract instance domain from publishable key for JWKS URL
        if self.clerk_publishable_key:
            try:
                # Clerk publishable keys are base64 encoded
                # Format: pk_test_<base64_encoded_domain> or pk_live_<base64_encoded_domain>
                if self.clerk_publishable_key.startswith('pk_test_') or self.clerk_publishable_key.startswith('pk_live_'):
                    # Extract the base64 part
                    prefix = 'pk_test_' if self.clerk_publishable_key.startswith('pk_test_') else 'pk_live_'
                    encoded_part = self.clerk_publishable_key[len(prefix):]
                    
                    # Decode the base64 to get the domain
                    try:
                        # Add padding if needed
                        missing_padding = len(encoded_part) % 4
                        if missing_padding:
                            encoded_part += '=' * (4 - missing_padding)
                        
                        decoded_bytes = base64.b64decode(encoded_part)
                        domain = decoded_bytes.decode('utf-8')
                        
                        # Remove any trailing characters that might be padding
                        if domain.endswith('$'):
                            domain = domain[:-1]
                        
                        self.jwks_url = f"https://{domain}/.well-known/jwks.json"
                        logger.info(f"Constructed JWKS URL: {self.jwks_url}")
                        
                    except Exception as decode_error:
                        logger.error(f"Failed to decode publishable key: {decode_error}")
                        self.jwks_url = None
                else:
                    logger.error("Invalid Clerk publishable key format - must start with pk_test_ or pk_live_")
                    self.jwks_url = None
            except Exception as e:
                logger.error(f"Error processing Clerk publishable key: {e}")
                self.jwks_url = None
        else:
            logger.warning("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY not found")
            self.jwks_url = None

    @lru_cache(maxsize=1)
    def get_jwks(self) -> Dict[str, Any]:
        """Fetch and cache JWKS from Clerk"""
        if not self.jwks_url:
            raise HTTPException(status_code=500, detail="JWKS URL not configured")
        
        try:
            response = requests.get(self.jwks_url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch JWKS: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch JWKS")

    def get_public_key(self, token_header: Dict[str, Any]) -> str:
        """Get the public key for JWT verification"""
        kid = token_header.get('kid')
        if not kid:
            raise HTTPException(status_code=401, detail="Token missing 'kid' in header")
        
        jwks = self.get_jwks()
        
        for key in jwks.get('keys', []):
            if key.get('kid') == kid:
                # Convert JWK to PEM format
                from cryptography.hazmat.primitives.asymmetric import rsa
                from cryptography.hazmat.primitives import serialization
                import base64
                
                # Decode the modulus and exponent
                n = base64.urlsafe_b64decode(key['n'] + '==')
                e = base64.urlsafe_b64decode(key['e'] + '==')
                
                # Convert to integers
                n_int = int.from_bytes(n, 'big')
                e_int = int.from_bytes(e, 'big')
                
                # Create RSA public key
                public_key = rsa.RSAPublicNumbers(e_int, n_int).public_key()
                
                # Convert to PEM format
                pem = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
                
                return pem.decode('utf-8')
        
        raise HTTPException(status_code=401, detail="Public key not found for token")

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode the JWT token"""
        if not self.clerk_secret_key:
            raise HTTPException(status_code=500, detail="Authentication not configured")
        
        try:
            # Decode header to get kid
            unverified_header = jwt.get_unverified_header(token)
            
            # Get public key
            public_key = self.get_public_key(unverified_header)
            
            # Verify and decode token
            payload = jwt.decode(
                token,
                public_key,
                algorithms=['RS256'],
                options={"verify_aud": False}  # Clerk doesn't use standard aud claim
            )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {e}")
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise HTTPException(status_code=401, detail="Token verification failed")

# Global instance
clerk_auth = ClerkAuth()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    payload = clerk_auth.verify_token(token)
    
    # Extract user information from token
    user_info = {
        "user_id": payload.get("sub"),  # Clerk user ID
        "email": payload.get("email"),
        "name": payload.get("name"),
        "image_url": payload.get("image_url"),
        "session_id": payload.get("sid"),
        "payload": payload  # Full payload for debugging
    }
    
    return user_info

async def get_optional_user(request: Request) -> Optional[Dict[str, Any]]:
    """Optional authentication - returns None if no valid token"""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header.split(" ")[1]
        payload = clerk_auth.verify_token(token)
        
        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "name": payload.get("name"),
            "image_url": payload.get("image_url"),
            "session_id": payload.get("sid"),
            "payload": payload
        }
    except:
        return None 