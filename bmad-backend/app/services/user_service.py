import os
import json
import uuid
import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any

class UserService:
    def __init__(self, storage_path: Path = None):
        if storage_path is None:
            # Default to a 'users' directory in the same parent directory as document_storage
            self.storage_path = Path(__file__).parent.parent.parent / "user_storage"
        else:
            self.storage_path = storage_path
        
        self.users_file = self.storage_path / "users.json"
        self._ensure_storage_exists()
        self._load_users()

    def _ensure_storage_exists(self) -> None:
        """Ensure the storage directory and users file exist."""
        os.makedirs(self.storage_path, exist_ok=True)
        if not self.users_file.exists():
            with open(self.users_file, "w") as f:
                json.dump({"users": []}, f)

    def _load_users(self) -> None:
        """Load users from the JSON file."""
        try:
            with open(self.users_file, "r") as f:
                self.users_data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # If file is empty or doesn't exist, initialize with empty users list
            self.users_data = {"users": []}
            self._save_users()
    
    def _save_users(self) -> None:
        """Save users to the JSON file."""
        with open(self.users_file, "w") as f:
            json.dump(self.users_data, f, indent=2)

    def _hash_password(self, password: str) -> str:
        """Hash a password for storing."""
        # In a real system, use a proper password hashing library like bcrypt
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(self, username: str, password: str, name: str, email: Optional[str] = None) -> Dict[str, Any]:
        """Create a new user."""
        # Check if username already exists
        if any(user["username"] == username for user in self.users_data["users"]):
            raise ValueError(f"Username '{username}' is already taken")
        
        user_id = str(uuid.uuid4())
        new_user = {
            "id": user_id,
            "username": username,
            "password_hash": self._hash_password(password),
            "name": name,
            "email": email,
            "created_at": datetime.now().isoformat(),
        }
        
        self.users_data["users"].append(new_user)
        self._save_users()
        
        # Return user without password_hash
        return {
            "id": new_user["id"],
            "username": new_user["username"],
            "name": new_user["name"],
            "email": new_user["email"],
        }

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get a user by username."""
        for user in self.users_data["users"]:
            if user["username"] == username:
                # Return a copy without the password hash
                user_data = {
                    "id": user["id"],
                    "username": user["username"],
                    "name": user["name"],
                    "email": user.get("email"),
                }
                # Include role if it exists
                if "role" in user:
                    user_data["role"] = user["role"]
                return user_data
        return None

    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user by username and password."""
        for user in self.users_data["users"]:
            if user["username"] == username and user["password_hash"] == self._hash_password(password):
                # Return a copy without the password hash
                user_data = {
                    "id": user["id"],
                    "username": user["username"],
                    "name": user["name"],
                    "email": user.get("email"),
                }
                # Include role if it exists
                if "role" in user:
                    user_data["role"] = user["role"]
                return user_data
        return None

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users (without password hashes)."""
        result = []
        for user in self.users_data["users"]:
            user_data = {
                "id": user["id"],
                "username": user["username"],
                "name": user["name"],
                "email": user.get("email"),
            }
            # Include role if it exists
            if "role" in user:
                user_data["role"] = user["role"]
            result.append(user_data)
        return result
        
    def is_admin(self, user_id: str) -> bool:
        """Check if a user has admin role."""
        for user in self.users_data["users"]:
            if user["id"] == user_id and user.get("role") == "admin":
                return True
        return False

    def update_user(self, user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a user's information."""
        for i, user in enumerate(self.users_data["users"]):
            if user["id"] == user_id:
                # Don't allow updating username or id
                safe_updates = {k: v for k, v in updates.items() if k not in ["id", "username", "password_hash"]}
                
                # Handle password update separately
                if "password" in updates:
                    self.users_data["users"][i]["password_hash"] = self._hash_password(updates["password"])
                
                self.users_data["users"][i].update(safe_updates)
                self._save_users()
                
                # Return updated user without password_hash
                return {
                    "id": self.users_data["users"][i]["id"],
                    "username": self.users_data["users"][i]["username"],
                    "name": self.users_data["users"][i]["name"],
                    "email": self.users_data["users"][i].get("email"),
                }
        
        return None

    def delete_user(self, user_id: str) -> bool:
        """Delete a user by ID."""
        for i, user in enumerate(self.users_data["users"]):
            if user["id"] == user_id:
                self.users_data["users"].pop(i)
                self._save_users()
                return True
        
        return False