# Standard library imports
import ast
import logging
import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Wristband imports 
from wristband.models import AuthConfig
from wristband.auth import Auth
from wristband.utils import to_bool, debug_request

# Local imports
from src import auth_router
from src.auth_middleware import SessionAuthMiddleware

# Load environment variables
load_dotenv()

def create_app() -> FastAPI:

    # Initialize the FastAPI app
    app = FastAPI()

    # SETUP LOGGING
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    root_logger: logging.Logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level))
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

    auth = Auth(auth_config)
    
    # Allow CORS
    origins: list[str] = [
        "*"
    ]

    # Add the session middleware to the app
    app.add_middleware(SessionAuthMiddleware)
    
    # Add debug request middleware only if log level is DEBUG
    if log_level == "DEBUG":
        @app.middleware("http")
        async def debug_request_middleware(request: Request, call_next):
            return await debug_request(request, call_next)
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Store auth in the app state
    app.state.auth = auth

    # Include routers
    app.include_router(auth_router.router, prefix='/api/auth')
    
    return app


app: FastAPI = create_app()

if __name__ == '__main__':
    uvicorn.run("run:app", host='0.0.0.0', port=8080, reload=True)