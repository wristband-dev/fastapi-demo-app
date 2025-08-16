from fastapi import APIRouter

from .auth_routes import router as auth_router
from .hello_world_routes import router as hello_world_router
from .nickname_routes import router as nickname_router
from .session_routes import router as session_router
from .token_routes import router as token_router

router = APIRouter()
router.include_router(auth_router, prefix="/api/auth")
router.include_router(hello_world_router, prefix="/api/hello")
router.include_router(nickname_router, prefix="/api/nickname")
router.include_router(session_router, prefix="/api/session")
router.include_router(token_router, prefix="/api/token")
