from fastapi import APIRouter, HTTPException, Depends, Header, status
from typing import Optional, Dict, Any
import logging
from app.services.user_service import UserService
from app.services.token_service import TokenService
from app.models import LoginRequest, RegisterRequest, AuthResponse
from app.security import get_current_user, is_admin

router = APIRouter(prefix="/auth", tags=["authentication"])

# Initialize services
user_service = UserService()
token_service = TokenService()

@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """Register a new user."""
    try:
        user = user_service.create_user(
            username=request.username,
            password=request.password,
            name=request.name,
            email=request.email
        )
        
        # Generate token for the new user
        token = token_service.create_token(user)
        
        return {
            "user": user,
            "token": token,
            "success": True
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Error during registration: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Login an existing user."""
    user = user_service.authenticate_user(
        username=request.username,
        password=request.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Generate token for the authenticated user
    token = token_service.create_token(user)
    
    return {
        "user": user,
        "token": token,
        "success": True
    }

@router.get("/protected", tags=["test"])
async def protected_route(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Test endpoint that requires authentication."""
    return {
        "status": "success",
        "message": f"Hello, {current_user['name']}! This is a protected route.",
        "user_id": current_user["id"]
    }

@router.get("/admin", tags=["test"])
async def admin_route(current_user: Dict[str, Any] = Depends(is_admin)):
    """Test endpoint that requires admin access."""
    return {
        "status": "success",
        "message": f"Hello, Admin {current_user['name']}! This is an admin-only route.",
        "user_id": current_user["id"]
    }

@router.get("/users", tags=["admin"])
async def list_users(current_user: Dict[str, Any] = Depends(is_admin)):
    """List all users - admin only access."""
    users = user_service.get_all_users()
    # Remove sensitive information like password hash
    sanitized_users = []
    for user in users:
        user_copy = user.copy()
        if "password" in user_copy:
            del user_copy["password"]
        sanitized_users.append(user_copy)
    
    return {
        "status": "success", 
        "users": sanitized_users,
        "count": len(sanitized_users)
    }

@router.get("/me", response_model=AuthResponse)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get the current authenticated user."""
    return {
        "user": current_user,
        "token": "",  # Token is not returned for security reasons
        "success": True
    }