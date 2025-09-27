# BMAD Authentication Implementation

This document outlines the authentication system implemented for the BMAD framework.

## Overview

The authentication system uses JWT (JSON Web Token) for secure token-based authentication. User information is stored in a file-based JSON database, with passwords hashed using SHA-256 (Note: In a production environment, use more secure password hashing like bcrypt).

## Features

- User registration and login
- Token-based authentication using JWT
- Role-based access control
- Protection of API endpoints
- Admin-only functionality

## Components

### User Management

- `UserService`: Handles user creation, retrieval, and authentication
- File-based storage in `user_storage/users.json`
- Password hashing using SHA-256

### Token Management

- `TokenService`: Handles JWT token creation and verification
- Includes user identity and role information in tokens
- Token expiration set to 24 hours by default

### Security Dependencies

- `get_current_user`: FastAPI dependency that extracts and validates user from JWT token
- `is_admin`: FastAPI dependency that checks if the current user has admin privileges

### API Endpoints

- `/api/auth/login`: Authenticate user and get token
- `/api/auth/register`: Create new user
- `/api/auth/me`: Get information about the current authenticated user
- `/api/auth/protected`: Test endpoint that requires authentication
- `/api/auth/admin`: Test endpoint that requires admin role
- `/api/auth/users`: Admin-only endpoint to list all users

## How to Test

### Start the Backend Server

```bash
cd bmad-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m app.main
```

### Test Authentication

Use the provided test script:

```bash
# Test with admin user
python test_auth.py admin admin12345

# Test with regular user
python test_auth.py user1 password123
```

### Client Integration

When integrating with a frontend client:

1. Send login credentials to `/api/auth/login`
2. Store the returned token
3. Include the token in all subsequent requests as:
   - HTTP Header: `Authorization: Bearer YOUR_TOKEN`

## Security Considerations

- This implementation is for development purposes
- In production, use:
  - HTTPS for all API requests
  - More secure password hashing (bcrypt)
  - Proper secret key management for JWT
  - Database-backed user storage
  - Shorter token expiration and refresh tokens