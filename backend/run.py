# Standard library imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging
import uvicorn

# Load environment variables BEFORE local imports
load_dotenv()

# Local imports
from middleware.auth_middleware import AuthMiddleware
from middleware.session_middleware import EncryptedSessionMiddleware
from routes import router as all_routes

def create_app() -> FastAPI:
    app = FastAPI()

    # Set up logging
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s in %(name)s: %(message)s")

    ########################################################################################
    # IMPORTANT: FastAPI middleware runs in reverse order of the way it is added below!!
    ########################################################################################

    # 1) Add the auth middleware to the app  
    app.add_middleware(AuthMiddleware)

    # 2) Add session middleware
    app.add_middleware(
        EncryptedSessionMiddleware,
        cookie_name="session",
        secret_key="a8f5f167f44f4964e6c998dee827110c",
        max_age=1800,  # 30 minutes
        path="/",
        same_site="lax",
        secure=False  # Set to True in production
    )

    # 3) Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3001"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    
    # Include API routers
    app.include_router(all_routes)

    return app

# This app instance is used when imported by Uvicorn
app = create_app()

if __name__ == '__main__':
    uvicorn.run("run:app", host="localhost", port=6001, reload=True)
