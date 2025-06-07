import logging
import os

from wristband.fastapi.auth import Auth
from wristband.models import AuthConfig
from wristband.utils import get_logger

logger: logging.Logger = get_logger()

def create_wristband_auth() -> Auth:
    auth_config = AuthConfig(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        wristband_application_vanity_domain=os.getenv("APPLICATION_VANITY_DOMAIN"),
        login_url="http://localhost:6001/api/auth/login",
        redirect_uri="http://localhost:6001/api/auth/callback",
        login_state_secret="dummyval-ab7d-4134-9307-2dfcc52f7475",
        dangerously_disable_secure_cookies=True,
        is_application_custom_domain_active=False,
        scopes=["openid", "offline_access", "email"],
    )
    logger.info("AuthConfig values:\n%s", auth_config)
    return Auth(auth_config)
