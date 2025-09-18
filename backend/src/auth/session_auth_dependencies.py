import logging
from typing import Optional

from fastapi import HTTPException, Request, Response, status
from wristband.fastapi_auth import TokenData

from auth.wristband import wristband_auth
from models.schemas import SessionData
from utils.csrf import update_csrf_cookie

logger = logging.getLogger(__name__)


async def require_session_auth(request: Request, response: Response) -> None:
    """
    Session authentication dependency for routes that need Wristband session validation.

    Validates user sessions via cookies, handles CSRF validation, and performs
    automatic token refresh when tokens are expired.

    Raises:
        HTTPException: 401 for unauthenticated sessions or token refresh failures
        HTTPException: 403 for CSRF token validation failures
    """
    logger.info(f"Executing session auth for: {request.method} {request.url.path}...")

    # WRISTBAND_TOUCHPOINT - AUTHENTICATION: Validate the user's authenticated session
    session_data: SessionData = request.state.session.get()
    if not session_data.is_authenticated:
        logger.warning(f"Auth validation failed for request to {request.url.path}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    # CSRF_TOUCHPOINT: Validate CSRF token
    header_csrf_token = request.headers.get("X-CSRF-TOKEN")
    if not session_data.csrf_token or not header_csrf_token or session_data.csrf_token != header_csrf_token:
        logger.warning(f"CSRF token validation failed for request to {request.url.path}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    try:
        # WRISTBAND_TOUCHPOINT - AUTHENTICATION: Refresh token only if it's expired
        new_token_data: Optional[TokenData] = await wristband_auth.refresh_token_if_expired(
            session_data.refresh_token, session_data.expires_at
        )
        if new_token_data:
            # Update session with new token data
            session_data.access_token = new_token_data.access_token
            session_data.refresh_token = new_token_data.refresh_token
            session_data.expires_at = new_token_data.expires_at

        # Update session and CSRF cookies
        request.state.session.update(response, session_data)
        update_csrf_cookie(response, session_data.csrf_token)

    except Exception as e:
        logger.exception(f"Session auth error during token refresh: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
