import os
from wristband.fastapi_auth import AuthConfig, WristbandAuth

# Explicitly define what can be imported
__all__ = ["require_jwt_auth", "require_session_auth", "wristband_auth"]

# Wristband authentication client for handling OAuth flows (login, callback, logout).
# and creating auth dependencies for protecting routes.
wristband_auth = WristbandAuth(
    AuthConfig(
        client_id=os.getenv("CLIENT_ID", ""),
        client_secret=os.getenv("CLIENT_SECRET", ""),
        wristband_application_vanity_domain=os.getenv("APPLICATION_VANITY_DOMAIN", ""),
        scopes=["openid", "offline_access", "email", "roles", "profile"],
        dangerously_disable_secure_cookies=True,  # IMPORTANT: Set this to False in Production!!
    )
)

# Session-based authentication dependency
# - Validates session cookies set by SessionMiddleware
# - Automatically refreshes expired access tokens using refresh tokens
# - Optionally handles CSRF token protection (via Token Synchronizer Pattern)
# - Use for web applications with cookie-based sessions
# Usage: @app.get("/protected", dependencies=[Depends(require_session_auth)])
# Or: async def route(session: Session = Depends(require_session_auth))
require_session_auth = wristband_auth.create_session_auth_dependency()

# JWT Bearer token authentication dependency
# - Validates JWT tokens from Authorization header (Bearer scheme)
# - Ideal for API endpoints and machine-to-machine authentication
# - Stateless authentication without session cookies
# Usage: @app.get("/api/data", dependencies=[Depends(require_jwt_auth)])
# Or: async def route(auth: JWTAuthResult = Depends(require_jwt_auth))
require_jwt_auth = wristband_auth.create_jwt_auth_dependency()
