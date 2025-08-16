# Standard library imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging
import uvicorn

# Load environment variables BEFORE local imports
load_dotenv()

# Local imports
from middleware.encrypted_session_middleware import EncryptedSessionMiddleware
from middleware.jwt_auth_middleware import JwtAuthMiddleware
from middleware.session_cookie_auth_middleware import SessionCookieAuthMiddleware
from routes import router as all_routes

def create_app() -> FastAPI:
    app = FastAPI()

    # Set up logging
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s in %(name)s: %(message)s")

    ########################################################################################
    # IMPORTANT: FastAPI middleware runs in reverse order of the way it is added below!!
    ########################################################################################

    # NOTE: In your Production app, you don't need both auth middleware types. You should choose the pattern
    # that best suits your needs with regards to protecting your endpoints. We use both types of auth
    # middleware here for demo purposes.

    # 1a) Add session cookie auth middleware (NOTE: applies to all non-auth "/api/*" routes except "/api/hello")
    app.add_middleware(SessionCookieAuthMiddleware)
    # 1b) Add JWT auth middleware (NOTE: only applies to "/api/hello" route)
    app.add_middleware(JwtAuthMiddleware)

    # 2) Add encrypted session middleware. In your Production app, you can use any kind of session library
    # or storage that you prefer. We use this cookie-based approach because it is lightweight and doesn't
    # require hardware/inrastructure.
    app.add_middleware(
        EncryptedSessionMiddleware,
        cookie_name="session",
        secret_key="a8f5f167f44f4964e6c998dee827110c",
        max_age=1800,  # 30 minutes
        path="/",
        same_site="lax",
        secure=True  # Set to True in production
    )

    # 3) Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:6001"],
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
    uvicorn.run("main:app", host="localhost", port=3001, reload=True)
