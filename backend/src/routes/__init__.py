from fastapi import APIRouter

from .auth_routes import router as auth_router
from .protected_routes import router as protected_router

router = APIRouter()

# Order matters here!
router.include_router(auth_router, prefix='/api/auth')
router.include_router(protected_router, prefix='/api')
