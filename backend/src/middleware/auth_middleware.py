# Standard library imports
from datetime import datetime, timedelta
from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
import logging

# Wristband imports
from wristband.fastapi_auth import TokenData

# Local imports
from auth.wristband import wristband_auth
from models.session_data import SessionData
from utils.csrf import update_csrf_cookie

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        path: str = request.url.path

        # Skip authentication for any public paths
        if path.startswith("/api/auth/") or path.startswith("/static/"):
            logger.info(f"Skipping auth middleware for: {request.method} {path}")
            return await call_next(request)

        # WRISTBAND_TOUCHPOINT - AUTHENTICATION
        # Validate the user's authenticated session
        session_data: SessionData = request.state.session.get()
        if not session_data.is_authenticated:
            return Response(status_code=status.HTTP_401_UNAUTHORIZED)
        
        # CSRF_TOUCHPOINT
        # Validate CSRF token
        header_csrf_token = request.headers.get("X-CSRF-TOKEN")
        if not session_data.csrf_token or not header_csrf_token or session_data.csrf_token != header_csrf_token:
            logger.warning(f"CSRF token validation failed for request to {path}")
            return Response(status_code=status.HTTP_403_FORBIDDEN)

        try:
            # WRISTBAND_TOUCHPOINT - AUTHENTICATION
            new_token_data: TokenData | None = wristband_auth.refresh_token_if_expired(
                session_data.refresh_token,
                session_data.expires_at
            )
            if new_token_data:
                # Update session with new token data
                logger.info("Token refreshed successfully")
                session_data.access_token = new_token_data.access_token
                session_data.refresh_token = new_token_data.refresh_token
                # Convert the "expiresIn" seconds into milliseconds from the epoch.
                session_data.expires_at = int(
                    (datetime.now() + timedelta(seconds=new_token_data.expires_in))
                    .timestamp() * 1000
                )

            # "Touch" the CSRF and session cookies. Saves new token data if refresh occured.
            response: Response = await call_next(request)
            request.state.session.update(response, session_data)
            update_csrf_cookie(response, session_data.csrf_token)
            return response
        except Exception as e:
            logger.exception(f"Auth middleware error during token refresh: {str(e)}")
            return Response(status_code=status.HTTP_401_UNAUTHORIZED)
