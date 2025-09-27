#!/usr/bin/env python

import json
import hashlib
import uuid
import os
from datetime import datetime
from pathlib import Path

def add_admin_user():
    # Define storage path and users file
    storage_path = Path(__file__).parent / "user_storage"
    users_file = storage_path / "users.json"
    
    # Ensure directory exists
    os.makedirs(storage_path, exist_ok=True)
    
    # Load existing users or create new structure
    if users_file.exists():
        try:
            with open(users_file, "r") as f:
                users_data = json.load(f)
        except json.JSONDecodeError:
            users_data = {"users": []}
    else:
        users_data = {"users": []}
    
    # Check if admin user already exists
    if any(user["username"] == "admin" for user in users_data["users"]):
        print("Admin user already exists!")
        return
    
    # Create admin user
    admin_user = {
        "id": str(uuid.uuid4()),
        "username": "admin",
        "password_hash": hashlib.sha256("admin12345".encode()).hexdigest(),
        "name": "Administrator",
        "email": "admin@bmad.example",
        "created_at": datetime.now().isoformat(),
        "role": "admin"  # Add admin role
    }
    
    # Add admin user to database
    users_data["users"].append(admin_user)
    
    # Save to file
    with open(users_file, "w") as f:
        json.dump(users_data, f, indent=2)
    
    print(f"Admin user created successfully with username 'admin' and password 'admin12345'")
    print(f"User ID: {admin_user['id']}")

if __name__ == "__main__":
    add_admin_user()