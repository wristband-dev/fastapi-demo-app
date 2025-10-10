import logging
from typing import cast

from fastapi import HTTPException, Request, status
from wristband.python_jwt import JWTPayload, JwtValidationResult

from auth.wristband import wristband_jwt

logger = logging.getLogger(__name__)


async def require_jwt_auth(request: Request) -> JWTPayload:
    """
    JWT authentication dependency for routes that need Wristband JWT validation.

    Validates JWT tokens from Authorization headers using Wristband JWT validator.

    Returns:
        JWTPayload object or Dict containing validated JWT payload

    Raises:
        HTTPException: 401 if token is missing, invalid, or validation fails
    """
    logger.info(f"Executing JWT validation for: {request.method} {request.url.path}...")

    try:
        # WRISTBAND_TOUCHPOINT: Extract and validate Bearer token from Authorization header
        auth_header = request.headers.get("authorization")
        token = wristband_jwt.extract_bearer_token(auth_header)
        result: JwtValidationResult = wristband_jwt.validate(token)

        if not result.is_valid:
            logger.warning(f"JWT validation failed: {result.error_message}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        # Return the validated payload for use in routes
        return cast(JWTPayload, result.payload)
    except Exception as e:
        logger.exception(f"JWT validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
