#!/usr/bin/env python

import requests
import json
import sys

# API base URL
BASE_URL = "http://localhost:8000/api"

def login(username, password):
    """Login and get auth token"""
    login_url = f"{BASE_URL}/auth/login"
    response = requests.post(
        login_url,
        json={"username": username, "password": password}
    )
    
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        print(response.text)
        return None
    
    data = response.json()
    token = data["token"]
    print(f"Login successful for user: {data['user']['username']}")
    return token

def test_protected_route(token):
    """Test the protected route with token"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/protected", headers=headers)
    
    if response.status_code == 200:
        print("Protected route access: Success")
        print(response.json())
    else:
        print(f"Protected route access failed: {response.status_code}")
        print(response.text)

def test_admin_route(token):
    """Test the admin-only route with token"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/admin", headers=headers)
    
    if response.status_code == 200:
        print("Admin route access: Success")
        print(response.json())
    else:
        print(f"Admin route access failed: {response.status_code}")
        print(response.text)

def test_users_list(token):
    """Test the users list endpoint (admin only)"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/users", headers=headers)
    
    if response.status_code == 200:
        print("Users list access: Success")
        users = response.json()["users"]
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"  - {user['username']} ({user['name']})")
    else:
        print(f"Users list access failed: {response.status_code}")
        print(response.text)

def main():
    if len(sys.argv) < 3:
        print("Usage: python test_auth.py <username> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    # Login and get token
    token = login(username, password)
    if not token:
        sys.exit(1)
    
    # Test protected endpoint
    test_protected_route(token)
    
    # Test admin-only endpoint
    test_admin_route(token)
    
    # Test users list endpoint
    test_users_list(token)

if __name__ == "__main__":
    main()