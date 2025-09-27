import jwt
import os
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

# This is a simple JWT implementation for demo purposes
# In production, use proper JWT libraries and secure secret management

class TokenService:
    def __init__(self):
        # In production, use a proper secret management system
        self.secret_key = os.getenv("JWT_SECRET_KEY", "bmad-secret-key")
        self.algorithm = "HS256"
        self.token_expire_minutes = 60 * 24  # 24 hours

    def create_token(self, user_data: Dict[str, Any]) -> str:
        """Create a JWT token for a user."""
        payload = user_data.copy()
        
        # Add expiration time
        expire = datetime.now() + timedelta(minutes=self.token_expire_minutes)
        payload.update({"exp": expire.timestamp()})
        
        # Ensure role is included if present
        if "role" in user_data:
            payload["role"] = user_data["role"]
        
        # Create token
        encoded_jwt = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify a JWT token and return the payload if valid."""
        try:
            # Decode and verify token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check if token is expired
            if "exp" in payload and payload["exp"] < time.time():
                return None
                
            return payload
        except jwt.PyJWTError:
            return None