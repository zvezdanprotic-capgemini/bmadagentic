#!/usr/bin/env python

import json
from pathlib import Path

def update_admin_role():
    # Define storage path and users file
    storage_path = Path(__file__).parent / "user_storage"
    users_file = storage_path / "users.json"
    
    # Load existing users
    if not users_file.exists():
        print("Users file not found!")
        return
    
    with open(users_file, "r") as f:
        users_data = json.load(f)
    
    # Find admin user and update role
    updated = False
    for user in users_data["users"]:
        if user["username"] == "admin":
            if "role" not in user or user["role"] != "admin":
                user["role"] = "admin"
                updated = True
                print(f"Added admin role to user '{user['username']}'")
    
    if not updated:
        print("Admin user not found or already has admin role")
        return
    
    # Save to file
    with open(users_file, "w") as f:
        json.dump(users_data, f, indent=2)
    
    print("Admin role updated successfully")

if __name__ == "__main__":
    update_admin_role()