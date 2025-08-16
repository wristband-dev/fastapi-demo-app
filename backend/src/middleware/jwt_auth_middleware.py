import logging
from typing import Awaitable, Callable

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from auth.wristband import wristband_jwt

logger = logging.getLogger(__name__)


class JwtAuthMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for JWT authentication using Wristband.

    Validates JWT tokens on protected routes and blocks unauthorized requests.
    Currently configured to protect only the "/api/hello" endpoint - customize
    the path logic for your application's needs.

    This middleware:
    - Extracts Bearer tokens from Authorization headers
    - Validates tokens using the Wristband JWT validator
    - Returns 401 Unauthorized for invalid/missing tokens
    - Allows requests to proceed for valid tokens

    Note: This middleware only performs validation - it does not store
    user information. Update the path checking logic to match your
    application's protected routes before using in production.
    """

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        path: str = request.url.path

        # Skip authentication for any public paths
        # NOTE: You should customize your allowed paths for this middleware in a real app.
        if path != "/api/hello":
            return await call_next(request)

        logger.info(f"Executing JWT validation middleware for: {request.method} {path}...")

        try:
            # WRISTBAND_TOUCHPOINT - AUTHENTICATION
            # Extract and validate Bearer token from Authorization header
            auth_header = request.headers.get("authorization")
            token = wristband_jwt.extract_bearer_token(auth_header)
            result = wristband_jwt.validate(token)

            if not result.is_valid:
                logger.exception(f"JWT validation middleware error: {result.error_message}")
                return Response(status_code=status.HTTP_401_UNAUTHORIZED)

            return await call_next(request)
        except Exception as e:
            logger.exception(f"JWT validation middleware error: {str(e)}")
            return Response(status_code=status.HTTP_401_UNAUTHORIZED)
