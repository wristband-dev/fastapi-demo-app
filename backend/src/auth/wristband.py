import os
from wristband.fastapi_auth import AuthConfig, WristbandAuth
from wristband.python_jwt import WristbandJwtValidator, WristbandJwtValidatorConfig, create_wristband_jwt_validator

# Explicitly define what can be imported
__all__ = ["require_session_auth", "wristband_auth", "wristband_jwt"]

# Wristband FastAPI Auth SDK Configuration
wristband_auth: WristbandAuth = WristbandAuth(
    AuthConfig(
        client_id=os.getenv("CLIENT_ID", ""),
        client_secret=os.getenv("CLIENT_SECRET", ""),
        wristband_application_vanity_domain=os.getenv("APPLICATION_VANITY_DOMAIN", ""),
        scopes=["openid", "offline_access", "email", "roles", "profile"],
        dangerously_disable_secure_cookies=True,  # IMPORTANT: Set this to False in Production!!
    )
)

# Validates sessions, handles CSRF protection, and automatically refreshes expired tokens
# Use with @router.get("/route", dependencies=[Depends(require_session_auth)])
require_session_auth = wristband_auth.create_session_auth_dependency()

# Wristband Python JWT SDK Configuration
wristband_jwt: WristbandJwtValidator = create_wristband_jwt_validator(
    WristbandJwtValidatorConfig(wristband_application_vanity_domain=os.getenv("APPLICATION_VANITY_DOMAIN", ""))
)
