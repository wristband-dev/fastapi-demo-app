import logging
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from wristband.fastapi_auth import SessionMiddleware

# Load environment variables BEFORE local imports
load_dotenv()

# Local imports
from routes import router as all_routes

DUMMY_SESSION_SECRET = "dummy_67f44f4964e6c998dee827110c"


def create_app() -> FastAPI:
    app = FastAPI()

    if not logging.getLogger().hasHandlers():
        logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s in %(name)s: %(message)s")
    
    # Enable DEBUG logging for Wristband SDK
    logging.getLogger("wristband.fastapi_auth").setLevel(logging.DEBUG)

    ########################################################################################
    # IMPORTANT: FastAPI middleware runs in reverse order of the way it is added below!!
    ########################################################################################

    # WRISTBAND_TOUCHPOINT: IMPORTANT - Set to `secure=True` in production!!
    # 1) Add encrypted cookie-based session middleware.
    app.add_middleware(SessionMiddleware, secret_key=DUMMY_SESSION_SECRET, secure=False)

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
