# Standard library imports
import logging
import os
import uvicorn
import argparse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Local imports
from auth.wristband_auth import create_wristband_auth
from middleware.auth_middleware import AuthMiddleware
from routes import router as all_routes

# Load environment variables
load_dotenv()

def create_app() -> FastAPI:
    # Initialize the FastAPI app
    app = FastAPI()

    # Set up logging (Only add handlers if none exist to prevent duplicate logging)
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    root_logger: logging.Logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    if not root_logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level))
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(name)s: %(message)s")
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # Check if any required env vars are missing
    required_env_vars: list[str] = ["CLIENT_ID", "CLIENT_SECRET", "APPLICATION_VANITY_DOMAIN"]
    missing_vars: list[str] = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {missing_vars}")
    
    # Add CORS middleware
    app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

    # Store Wristband Auth instance in the app state
    app.state.auth = create_wristband_auth()

    # Add the auth middleware to the app
    app.add_middleware(AuthMiddleware)
    
    # Include API routers
    app.include_router(all_routes)

    return app

# This app instance is used when imported by Uvicorn
app = create_app()

if __name__ == '__main__':
    # init parser
    parser = argparse.ArgumentParser(description='Run the FastAPI application')

    # add args
    parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='Set the logging level')
    parser.add_argument('--debug', action='store_true', help='Set log level to DEBUG (overrides --log-level)')
    parser.add_argument('--host', type=str, help='Host to bind the server to')
    parser.add_argument('--port', type=int, help='Port to bind the server to')

    # parse args
    args = parser.parse_args()

    # Set the log level environment variable BEFORE app creation
    if args.debug:
        os.environ["LOG_LEVEL"] = "DEBUG"
    elif args.log_level:
        os.environ["LOG_LEVEL"] = args.log_level

    # Run the app
    # hot_reload: bool = False if args.prod else True
    uvicorn.run("run:app", host="localhost", port=6001, reload=True)
