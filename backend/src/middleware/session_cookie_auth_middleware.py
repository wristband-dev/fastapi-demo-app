import logging
from datetime import datetime, timedelta
from typing import Awaitable, Callable, Optional

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from wristband.fastapi_auth import TokenData

from auth.wristband import wristband_auth
from models.session_data import SessionData
from utils.csrf import update_csrf_cookie

logger = logging.getLogger(__name__)


class SessionCookieAuthMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for session-based authentication using Wristband.

    Validates user sessions via cookies and handles token refresh for authenticated requests.
    Skips authentication for auth endpoints (/api/auth/*), static files (/static/*),
    and the hello endpoint (/api/hello).

    This middleware performs:
    - Session validation via cookies
    - CSRF token validation against X-CSRF-TOKEN header
    - Automatic token refresh when tokens are expired
    - Session and CSRF cookie updates after successful requests

    Returns:
    - 401 Unauthorized for unauthenticated sessions or token refresh failures
    - 403 Forbidden for CSRF token validation failures
    - Continues request processing for valid authenticated sessions

    Note: Customize the path exclusion logic for your application's
    public routes before using in production.
    """

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        path: str = request.url.path

        # Skip authentication for any public paths or the Hello World path
        # NOTE: You should customize your allowed paths for this middleware in a real app.
        if path.startswith("/api/auth/") or path.startswith("/static/") or path == "/api/hello":
            return await call_next(request)

        logger.info(f"Executing auth middleware for: {request.method} {path}...")

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
            new_token_data: Optional[TokenData] = await wristband_auth.refresh_token_if_expired(
                session_data.refresh_token, session_data.expires_at
            )
            if new_token_data:
                # Update session with new token data
                logger.info("Token refreshed successfully")
                session_data.access_token = new_token_data.access_token
                session_data.refresh_token = new_token_data.refresh_token
                # Convert the "expiresIn" seconds into milliseconds from the epoch.
                session_data.expires_at = int(
                    (datetime.now() + timedelta(seconds=new_token_data.expires_in)).timestamp() * 1000
                )

            # "Touch" the CSRF and session cookies. Saves new token data if refresh occured.
            response: Response = await call_next(request)
            request.state.session.update(response, session_data)
            update_csrf_cookie(response, session_data.csrf_token)
            return response
        except Exception as e:
            logger.exception(f"Auth middleware error during token refresh: {str(e)}")
            return Response(status_code=status.HTTP_401_UNAUTHORIZED)
