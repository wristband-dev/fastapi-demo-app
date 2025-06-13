from fastapi import APIRouter

from .auth_routes import router as auth_router
from .nickname_routes import router as nickname_router
from .session_routes import router as session_router

router = APIRouter()
router.include_router(auth_router, prefix='/api/auth')
router.include_router(nickname_router, prefix='/api/nickname')
router.include_router(session_router, prefix='/api/session')
