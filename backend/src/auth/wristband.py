import os

from wristband.fastapi_auth import AuthConfig, WristbandAuth
from wristband.python_jwt import WristbandJwtValidator, WristbandJwtValidatorConfig, create_wristband_jwt_validator

# Explicitly define what can be imported
__all__ = ["wristband_auth", "wristband_jwt"]

# Wristband FastAPI Auth SDK Configuration
wristband_auth: WristbandAuth = WristbandAuth(
    AuthConfig(
        client_id=os.getenv("CLIENT_ID", ""),
        client_secret=os.getenv("CLIENT_SECRET", ""),
        wristband_application_vanity_domain=os.getenv("APPLICATION_VANITY_DOMAIN", ""),
    )
)

# Wristband Python JWT SDK Configuration
wristband_jwt: WristbandJwtValidator = create_wristband_jwt_validator(
    WristbandJwtValidatorConfig(wristband_application_vanity_domain=os.getenv("APPLICATION_VANITY_DOMAIN", ""))
)
