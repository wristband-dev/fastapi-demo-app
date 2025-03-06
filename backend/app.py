import ast
import logging
import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()


from src.sdk.models import AuthConfig
from src.sdk.auth_service import AuthService
from src.api.auth_route import auth_route
from src.sdk.utils import to_bool


def create_app() -> Flask:

    app = Flask(__name__)

    # SETUP LOGGING
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(name)s: %(message)s")
    console_handler.setFormatter(formatter)

    if not root_logger.handlers:
        root_logger.addHandler(console_handler)

    # Required environment variables:
    required_env_vars: list[str] = [
        "CLIENT_ID", 
        "CLIENT_SECRET", 
        "LOGIN_STATE_SECRET", 
        "LOGIN_URL", 
        "REDIRECT_URI",
        "APP_HOME_URL",
        "SESSION_COOKIE_SECRET"
    ]
    
    # Check if any required var is missing
    missing_vars: list[str] = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {missing_vars}")

    # Safely parse SCOPES as a Python list (e.g. "['openid','offline_access','email']")
    raw_scopes: str = os.getenv("SCOPES", "['openid', 'offline_access', 'email']")
    try:
        scopes_list = ast.literal_eval(raw_scopes)
        if not isinstance(scopes_list, list):
            raise ValueError
    except Exception:
        raise ValueError("SCOPES must be a valid Python list literal (e.g. \"['openid','email']\").")

    # Convert string-based boolean environment variables

    auth_config = AuthConfig(
        client_id=os.getenv("CLIENT_ID", ""),
        client_secret=os.getenv("CLIENT_SECRET", ""),
        login_state_secret=os.getenv("LOGIN_STATE_SECRET", ""),
        login_url=os.getenv("LOGIN_URL", ""),
        redirect_uri=os.getenv("REDIRECT_URI", ""),
        wristband_application_domain=os.getenv("WRISTBAND_APPLICATION_DOMAIN", ""),
        custom_application_login_page_url=os.getenv("CUSTOM_APPLICATION_LOGIN_PAGE_URL", ""),
        dangerously_disable_secure_cookies=to_bool(os.getenv("DANGEROUSLY_DISABLE_SECURE_COOKIES", "False")),
        root_domain=os.getenv("ROOT_DOMAIN", ""),
        scopes=scopes_list,
        use_custom_domains=to_bool(os.getenv("USE_CUSTOM_DOMAINS", "False")),
        use_tenant_subdomains=to_bool(os.getenv("USE_TENANT_SUBDOMAINS", "False")),
    )

    auth_service = AuthService(auth_config)
    app.config["auth_service"] = auth_service # allow the auth service to be accessed by any route

    app.register_blueprint(auth_route, url_prefix='/api/auth')

    return app
    
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8080, debug=True)