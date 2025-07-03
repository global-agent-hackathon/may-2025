# AdGenius Authentication Flow

This document describes the authentication flow for the AdGenius application, which uses Google OAuth for user authentication.

## Overview

The authentication flow uses a token-based approach with JWTs:

1. User initiates login via Google OAuth
2. Server authenticates with Google and generates a JWT token
3. Frontend stores the token in localStorage and uses it for subsequent requests
4. Token validation is performed by the server on protected endpoints

## Detailed Flow

### Login Process

1. **Frontend Initiates Login**:

   - User clicks "Sign in with Google" button
   - The current path is saved to be used as the redirect destination after authentication
   - Frontend calls `/api/v1/auth/login/google` endpoint with the redirect URL

2. **Server Generates OAuth URL**:

   - Server encodes the redirect URL in the state parameter
   - Returns the Google OAuth URL

3. **Google Authentication**:

   - User is redirected to Google to authenticate
   - User grants permissions to the application
   - Google redirects back to our callback URL with an authorization code

4. **Server Processes Callback**:

   - Server exchanges the code for Google tokens
   - User information is retrieved from Google
   - Server creates or updates the user in the database
   - A JWT token is generated for the user
   - Server redirects to frontend's auth callback endpoint with the token and redirect path

5. **Frontend Callback Handling**:
   - Frontend stores the JWT token in localStorage
   - User information is validated via a token validation API call
   - User is redirected to the original path (with special handling for login page)
   - If the original path was the login page, user is redirected to home page instead

### Token Usage

- The token is stored in localStorage
- It's automatically added to all API requests via an Axios interceptor
- The server validates the token for all protected endpoints

### Logout Process

1. User clicks logout button
2. Frontend calls the logout API endpoint
3. Frontend removes the token from localStorage
4. User is redirected to the login page

## API Endpoints

### `/api/v1/auth/login/google`

- **Method**: GET
- **Query Parameters**: `redirect_url` (optional)
- **Response**: `{ "auth_url": "https://accounts.google.com/..." }`
- **Note**: If `redirect_url` is "/login", user will be redirected to "/" after authentication

### `/api/v1/auth/callback`

- **Method**: GET
- **Query Parameters**:
  - `code`: Authorization code from Google
  - `state`: Encoded state including redirect URL
- **Action**: Redirects to frontend with token and redirect path (avoiding login page redirects)

### `/api/v1/auth/validate`

- **Method**: GET
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{ "valid": true, "user": {...} }` or `{ "valid": false }`

### `/api/v1/auth/me`

- **Method**: GET
- **Headers**: `Authorization: Bearer <token>`
- **Response**: User profile information

### `/api/v1/auth/logout`

- **Method**: POST
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{ "success": true, "message": "Logged out successfully" }`

## Security Considerations

- JWT tokens have a default expiration of 24 hours
- Tokens should only be transmitted over HTTPS in production
- The frontend should handle token expiration gracefully
- Sensitive operations should require re-authentication
- Token validation is performed on every protected API request

## Configuration

Authentication settings can be configured in the `.env` file:

```
SECRET_KEY="your-secret-key-replace-this-in-production"
GOOGLE_CLIENT_ID="your-google-client-id"
GOOGLE_CLIENT_SECRET="your-google-client-secret"
GOOGLE_REDIRECT_URI="http://localhost:8000/api/v1/auth/callback"
FRONTEND_URL="http://localhost:5173"
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```
