from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from models.session_data import SessionData
from utils.session import get_session_data

class SimpleSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            request.state.session = get_session_data(request)
        except Exception as e:
            # Set a fallback empty session
            request.state.session = SessionData.empty()
        
        response = await call_next(request)
        return response
