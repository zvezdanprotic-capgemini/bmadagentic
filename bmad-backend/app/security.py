from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any

from app.services.token_service import TokenService
from app.services.user_service import UserService

security = HTTPBearer()
token_service = TokenService()
user_service = UserService()

async def get_current_user(
    authorization: Optional[str] = Header(None), 
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency to get the current authenticated user.
    Can be used with either Authorization header or Bearer token in security scheme.
    
    Returns the user data from the token payload.
    """
    # First try from security scheme
    token = None
    if credentials:
        token = credentials.credentials
    # Then try from Authorization header
    elif authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = token_service.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "id": payload["id"],
        "username": payload["username"],
        "name": payload["name"],
        "email": payload.get("email")
    }

def is_admin(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Dependency to check if the current user is an admin.
    Checks if the user has the admin role or is explicitly the admin user.
    
    Returns the user data if the user is an admin.
    """
    # Check if user has admin role in token
    has_admin_role = user.get("role") == "admin"
    # Or check directly in the database
    is_admin_in_db = user_service.is_admin(user["id"])
    
    if not (has_admin_role or is_admin_in_db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Admin privileges required.",
        )
    return user