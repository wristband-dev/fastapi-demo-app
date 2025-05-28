# Standard library imports
import ast
import logging
import os
import uvicorn
import argparse
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Wristband imports 
from wristband.fastapi.auth import Auth
from wristband.models import AuthConfig
from wristband.utils import to_bool, debug_request

# Local imports
from src import auth_router
from src.auth_middleware import SessionAuthMiddleware
from src.config_utils import get_config_value

# Load environment variables
load_dotenv()

def create_app() -> FastAPI:
    # Initialize the FastAPI app
    app = FastAPI()

    # SETUP LOGGING
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    root_logger: logging.Logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    
    # Only add handlers if none exist to prevent duplicate logging
    if not root_logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level))
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(name)s: %(message)s")
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # Required environment variables:
    required_env_vars: list[str] = [
        "CLIENT_ID", 
        "CLIENT_SECRET"
    ]
    
    # Check if any required var is missing
    missing_vars: list[str] = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {missing_vars}")

    # Safely parse SCOPES as a Python list
    raw_scopes: str = get_config_value("wristband", "scopes")

    try:
        # Split the comma-separated string and strip whitespace
        scopes_list = [scope.strip() for scope in raw_scopes.split(',')]
        if not scopes_list or any(not scope for scope in scopes_list):
            raise ValueError("Empty scope found")
    except Exception:
        raise ValueError("SCOPES must be a comma-separated string (e.g. \"openid, email, offline_access\").")
    
    # get urls
    app_host: str = get_config_value("app", "host")
    backend_port: int = int(get_config_value("backend", "port"))
    backend_login_url_suffix: str = get_config_value("backend", "login_url_suffix")
    backend_redirect_uri_suffix: str = get_config_value("backend", "redirect_uri_suffix")


    login_url: str = f"{app_host}:{backend_port}/{backend_login_url_suffix}"
    redirect_uri: str = f"{app_host}:{backend_port}/{backend_redirect_uri_suffix}"

    # Convert string-based boolean environment variables
    auth_config = AuthConfig(
        client_id=os.getenv("CLIENT_ID", ""),
        client_secret=os.getenv("CLIENT_SECRET", ""),
        login_state_secret=get_config_value("secrets", "login_state_secret"),
        login_url=login_url,
        redirect_uri=redirect_uri,
        wristband_application_vanity_domain=os.getenv("APPLICATION_VANITY_DOMAIN", ""),
        custom_application_login_page_url=get_config_value("wristband", "custom_application_login_page_url"),
        dangerously_disable_secure_cookies=to_bool(get_config_value("wristband", "dangerously_disable_secure_cookies")),
        root_domain=get_config_value("wristband", "root_domain"),
        scopes=scopes_list,
        use_custom_domains=to_bool(get_config_value("wristband", "use_custom_domains")),
        use_tenant_subdomains=to_bool(get_config_value("wristband", "use_tenant_subdomains")),
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


# This app instance is used when imported by Uvicorn
app = create_app()


if __name__ == '__main__':
    # init parser
    parser = argparse.ArgumentParser(description='Run the FastAPI application')

    # add args
    parser.add_argument('--log-level', type=str, choices=[
            'DEBUG', 
            'INFO', 
            'WARNING', 
            'ERROR', 
            'CRITICAL'
        ],
        help='Set the logging level'
    )
    parser.add_argument('--debug', action='store_true', help='Set log level to DEBUG (overrides --log-level)')
    parser.add_argument('--host', type=str, help='Host to bind the server to')
    parser.add_argument('--port', type=int, help='Port to bind the server to')

    # environments
    parser.add_argument('--prod', action='store_true', help='Use the production database')
    parser.add_argument('--dev', action='store_true', help='Use the development database')
    
    # parse args
    args = parser.parse_args()

    # Set the log level environment variable BEFORE app creation
    if args.debug:
        os.environ["LOG_LEVEL"] = "DEBUG"
    elif args.log_level:
        os.environ["LOG_LEVEL"] = args.log_level
    
    # get host and port
    host: str = args.host if args.host else get_config_value("app", "host")
    host = host if host != "http://localhost" else "0.0.0.0"
    port: int = args.port if args.port else int(get_config_value("backend", "port"))
    
    if args.prod:
        uvicorn.run("run:app", host=host, port=port, reload=False)
    else:
        uvicorn.run("run:app", host=host, port=port, reload=True)