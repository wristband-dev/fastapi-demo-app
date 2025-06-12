# Standard library imports
from datetime import datetime, timedelta
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

# Wristband imports
from wristband.models import TokenData

# Local imports
from auth.wristband import wristband_auth
from models.session_data import SessionData
from utils.csrf import update_csrf_cookie
from utils.session import update_session_cookie

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response | JSONResponse:
        path: str = request.url.path

        # Skip authentication for public paths
        if path.startswith("/api/auth/") or path.startswith("/static/"):
            logger.info(f"Skipping auth middleware for: {request.method} {path}")
            return await call_next(request)

        # Validate the user's authenticated session
        session_data: SessionData = request.state.session
        if not session_data.is_authenticated:
            return Response(status_code=status.HTTP_401_UNAUTHORIZED)
        
        # CSRF_TOUCHPOINT
        # Validate CSRF token
        header_csrf_token = request.headers.get("X-CSRF-TOKEN")
        if not session_data.csrf_token or not header_csrf_token or session_data.csrf_token != header_csrf_token:
            logger.warning(f"CSRF token validation failed for request to {path}")
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "CSRF validation failed"})

        try:
            # WRISTBAND_TOUCHPOINT - AUTHENTICATION
            new_token_data: TokenData | None = wristband_auth.refresh_token_if_expired(session_data.refresh_token, session_data.expires_at)
            if new_token_data:
                logger.info("Token refreshed successfully")
                # Update session with new token data
                session_data.access_token = new_token_data.access_token
                session_data.refresh_token = new_token_data.refresh_token
                # Convert the "expiresIn" seconds into milliseconds from the epoch.
                session_data.expires_at = int(
                    (datetime.now() + timedelta(seconds=new_token_data.expires_in))
                    .timestamp() * 1000
                )
                # Set the request state with session data for usage in route handlers
                request.state.session_data = session_data
                        
            # "Touch" the CSRF and session cookies. Saves new token data if refresh occured.
            response: Response = await call_next(request)
            update_session_cookie(response, session_data)
            update_csrf_cookie(response, session_data.csrf_token)
            return response
        except Exception as e:
            logger.exception(f"Auth middleware error: {str(e)}")
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Token refresh failed"})
