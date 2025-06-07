# Standard library imports
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

# Wristband imports
from wristband.models import TokenData
from wristband.models import SessionData
from wristband.fastapi.auth import Auth
from wristband.utils import get_logger

# Local imports
from utils.session import get_session_data, update_session_cookie

logger: logging.Logger = get_logger()

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response | JSONResponse:
        path: str = request.url.path
        logger.info(f"Processing request to path: {path}")

        # Skip authentication for public paths
        if path.startswith("/api/auth/") or path.startswith("/static/"):
            logger.info(f"Skipping authentication")
            return await call_next(request)
        
        # Get the user's session data
        session_data: SessionData | None = get_session_data(request)
        if not session_data:
            logger.error("No authenticated session found.")
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "No authenticated session found."})
            
        # Check if access token exists
        if not session_data.access_token:
            logger.warning("No access token found in session data")
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "No access token in session"})
        
        # Validate CSRF token
        csrf_cookie = request.cookies.get("CSRF-TOKEN")
        header_csrf_token = request.headers.get("X-CSRF-TOKEN")
        if not csrf_cookie or not header_csrf_token or csrf_cookie != header_csrf_token:
            logger.warning(f"CSRF token validation failed for request to {path}")
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "CSRF validation failed"})
        logger.debug("CSRF token validation successful")
                
        # Check if access token is expired
        auth: Auth = request.app.state.auth
        if not auth.is_expired(session_data.expires_at):
            logger.info(f"Access token is still valid. Proceeding with request...")
            return await call_next(request)

        # Try to refresh the token
        try:
            logger.info("Access token is expired, attempting to refresh")
            new_token_data: TokenData | None = auth.refresh_token_if_expired(session_data.refresh_token, session_data.expires_at)
                    
            if new_token_data:
                logger.info("Token refreshed successfully")
                # Update session with new token data
                session_data.access_token = new_token_data.access_token
                session_data.refresh_token = new_token_data.refresh_token
                session_data.expires_at = new_token_data.expires_at
                        
                # Set the request state with session data for usage in route handlers
                request.state.session_data = session_data
                        
            # Update the session cookie with new token data
            response: Response = await call_next(request)
            update_session_cookie(response, session_data, False)

            # Execute the route handler
            logger.debug(f"Authentication successful for request to {path}")
            return response
        except Exception as e:
            logger.exception(f"Session middleware error: {str(e)}")
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Token refresh failed"})
