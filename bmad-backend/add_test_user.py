#!/usr/bin/env python

import json
import hashlib
import uuid
import os
from datetime import datetime
from pathlib import Path

def add_test_user(username, password, name, email=None):
    # Define storage path and users file
    storage_path = Path(__file__).parent / "user_storage"
    users_file = storage_path / "users.json"
    
    # Ensure directory exists
    os.makedirs(storage_path, exist_ok=True)
    
    # Load existing users
    with open(users_file, "r") as f:
        users_data = json.load(f)
    
    # Check if user already exists
    if any(user["username"] == username for user in users_data["users"]):
        print(f"User '{username}' already exists!")
        return
    
    # Create user
    new_user = {
        "id": str(uuid.uuid4()),
        "username": username,
        "password_hash": hashlib.sha256(password.encode()).hexdigest(),
        "name": name,
        "email": email,
        "created_at": datetime.now().isoformat(),
    }
    
    # Add user to database
    users_data["users"].append(new_user)
    
    # Save to file
    with open(users_file, "w") as f:
        json.dump(users_data, f, indent=2)
    
    print(f"User '{username}' created successfully with password '{password}'")
    print(f"User ID: {new_user['id']}")

if __name__ == "__main__":
    # Add a regular test user
    add_test_user("user1", "password123", "Test User", "user1@example.com")