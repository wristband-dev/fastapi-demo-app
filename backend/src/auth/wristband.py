import os

from wristband.fastapi_auth import AuthConfig, WristbandAuth

# Explicitly define what can be imported
__all__ = ['wristband_auth']

def _create_wristband_auth() -> WristbandAuth:
    auth_config = AuthConfig(
        client_id=os.getenv("CLIENT_ID", ""),
        client_secret=os.getenv("CLIENT_SECRET", ""),
        wristband_application_vanity_domain=os.getenv("APPLICATION_VANITY_DOMAIN", ""),
        login_url="http://localhost:6001/api/auth/login",
        redirect_uri="http://localhost:6001/api/auth/callback",
        login_state_secret="dummyval-ab7d-4134-9307-2dfcc52f7475",
        dangerously_disable_secure_cookies=True,
        is_application_custom_domain_active=False,
        scopes=["openid", "offline_access", "email"],
    )
    return WristbandAuth(auth_config)

wristband_auth: WristbandAuth = _create_wristband_auth()
