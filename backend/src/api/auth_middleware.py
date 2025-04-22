import os
from typing import Any, Optional, List
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from wristband.models import SessionData
from wristband.auth import Auth
from wristband.utils import CookieEncryptor
from wristband.utils import to_bool

# Public paths that don't require authentication
PUBLIC_PATHS: List[str] = [
    "/api/auth/login",
    "/api/auth/callback",
    "/api/auth/logout",
    "/api/auth/test_decrypt_cookie",
    "/api/auth/session"
]

class SessionAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip authentication for public paths
        path = request.url.path
        if path in PUBLIC_PATHS or path.startswith("/static/"):
            return await call_next(request)
            
        try:
            # Get session cookie
            session_secret_cookie: Optional[str] = os.getenv("SESSION_COOKIE_SECRET")
            if session_secret_cookie is None:
                raise ValueError("Missing environment variable: SESSION_COOKIE_SECRET")
            
            # Check if the session cookie exists
            session_cookie = request.cookies.get("session")
            if not session_cookie:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "No session found"}
                )
                
            # Decrypt the session cookie
            session_data_dict = CookieEncryptor(session_secret_cookie).decrypt(session_cookie)
            session_data = SessionData.from_dict(session_data_dict)
            
            # Check if access token exists
            if not session_data.access_token:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "No access token in session"}
                )
                
            # Check if access token is expired
            auth: Auth = request.app.state.auth
            if auth.is_expired(session_data.expires_at):
                # Try to refresh the token if refresh token exists
                if session_data.refresh_token:
                    # Refresh the token
                    new_token_data = auth.refresh_token_if_expired(
                        session_data.refresh_token, 
                        session_data.expires_at
                    )
                    
                    if new_token_data:
                        # Update session with new token data
                        session_data.access_token = new_token_data.access_token
                        session_data.refresh_token = new_token_data.refresh_token
                        session_data.expires_at = new_token_data.expires_at
                        
                        # Set the request state with session data for usage in route handlers
                        request.state.session_data = session_data
                        
                        # Execute the route handler
                        response = await call_next(request)
                        
                        # Update the session cookie with new token data
                        encrypted_session = CookieEncryptor(session_secret_cookie).encrypt(
                            session_data.to_dict()
                        )
                        
                        secure: bool = not to_bool(os.getenv("DANGEROUSLY_DISABLE_SECURE_COOKIES", "False"))
                        response.set_cookie(
                            key="session",
                            value=encrypted_session,
                            secure=secure,
                            httponly=True,
                            samesite="lax"
                        )
                        
                        return response
                    else:
                        # Refresh failed
                        return JSONResponse(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            content={"detail": "Token refresh failed"}
                        )
                else:
                    # No refresh token
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "Access token expired and no refresh token available"}
                    )
            
            # Token is valid, set session data in request state for use in route handlers
            request.state.session_data = session_data
            return await call_next(request)
            
        except Exception as e:
            print(f"Session middleware error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": f"Authentication error: {str(e)}"}
            )