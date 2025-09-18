import logging
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables BEFORE local imports
load_dotenv()

# Local imports
from middleware.encrypted_session_middleware import EncryptedSessionMiddleware
from routes import router as all_routes


def create_app() -> FastAPI:
    app = FastAPI()

    if not logging.getLogger().hasHandlers():
        logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s in %(name)s: %(message)s")

    ########################################################################################
    # IMPORTANT: FastAPI middleware runs in reverse order of the way it is added below!!
    ########################################################################################

    # 1) Add encrypted session middleware. In your Production app, you can use any kind of session library
    # or storage that you prefer. We use this cookie-based approach because it is lightweight and doesn't
    # require hardware/infrastructure.
    app.add_middleware(
        EncryptedSessionMiddleware,
        cookie_name="session",
        secret_key="dummy_67f44f4964e6c998dee827110c",
        max_age=1800,  # 30 minutes
        path="/",
        same_site="lax",
        secure=False  # IMPORTANT: Set to True in production!!
    )

    # 2) Add CORS middleware
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
