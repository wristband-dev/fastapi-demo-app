from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Literal, cast
import logging

from wristband.fastapi_auth import SessionEncryptor
from models.session_data import SessionData

__all__ = ['EncryptedSessionMiddleware']

logger = logging.getLogger(__name__)
SameSiteOptions = Literal["lax", "strict", "none"]

class _SessionManager:
    """Session manager that provides session operations"""
    
    def __init__(
        self,
        encryptor: SessionEncryptor,
        cookie_name: str,
        max_age: int,
        path: str,
        same_site: SameSiteOptions,
        http_only: bool,
        secure: bool
    ):
        self.encryptor = encryptor
        self.cookie_name = cookie_name
        self.max_age = max_age
        self.path = path
        self.same_site: SameSiteOptions = same_site
        self.http_only = http_only
        self.secure = secure
        self._session_data: SessionData = SessionData.empty()
    
    def get(self) -> SessionData:
        """Get current session data"""
        return self._session_data
    
    def set_data(self, session_data: SessionData) -> None:
        """Set session data internally"""
        self._session_data = session_data
    
    def update(self, response: Response, session_data: SessionData) -> None:
        """Update session data and set cookie on response immediately"""
        self._session_data = session_data
        encrypted_value = self.encryptor.encrypt(session_data.to_dict())
        
        response.set_cookie(
            key=self.cookie_name,
            value=encrypted_value,
            max_age=self.max_age,
            path=self.path,
            secure=self.secure,
            httponly=self.http_only,
            samesite=self.same_site
        )
    
    def delete(self, response: Response) -> None:
        """Delete session cookie and clear session data immediately"""
        self._session_data = SessionData.empty()
        
        response.set_cookie(
            key=self.cookie_name,
            value='',
            max_age=0,
            path=self.path,
            secure=self.secure,
            httponly=self.http_only,
            samesite=self.same_site
        )

class EncryptedSessionMiddleware(BaseHTTPMiddleware):
    """
    Session middleware that provides encrypted cookie-based sessions.
    
    Usage:
        app.add_middleware(
            EncryptedSessionMiddleware,
            cookie_name="session",
            secret_key="your-secret-key-here",
            max_age=1800,  # 30 minutes
            path="/",
            same_site="lax",
            http_only=True,  # Set to True in production
            secure=False,    # Set to True in production with HTTPS
        )
    
    In routes:
        # Get current session data
        current_session = request.state.session.get()
        
        # Update session (clean API!)
        new_data = SessionData(user_id="123", ...)
        request.state.session.update(response, new_data)
        
        # Delete session (clean API!)
        request.state.session.delete(response)
    """
    
    def __init__(
        self,
        app,
        cookie_name: str = "session",
        secret_key: str = "",
        max_age: int = 1800,  # 30 minutes
        path: str = "/",
        same_site: Literal["lax", "strict", "none"] = "lax",
        http_only: bool = True,
        secure: bool = False,
    ):
        super().__init__(app)
        
        if not secret_key:
            raise ValueError("secret_key is required for session encryption")
        
        self.cookie_name = cookie_name
        self.max_age = max_age
        self.path = path
        self.same_site: SameSiteOptions = same_site
        self.http_only = http_only
        self.secure = secure
        self.encryptor = SessionEncryptor(secret_key)
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Create session manager
        session_manager = _SessionManager(
            encryptor=self.encryptor,
            cookie_name=self.cookie_name,
            max_age=self.max_age,
            path=self.path,
            same_site=self.same_site,
            http_only=self.http_only,
            secure=self.secure
        )
        
        # Try to load existing session
        try:
            session_cookie = request.cookies.get(self.cookie_name)
            if session_cookie:
                session_data_dict = self.encryptor.decrypt(session_cookie)
                session_data = SessionData.from_dict(session_data_dict)
                session_manager.set_data(session_data)
            else:
                session_manager.set_data(SessionData.empty())
        except Exception as e:
            logger.error(f"Failed to decrypt session cookie: {str(e)}")
            session_manager.set_data(SessionData.empty())
        
        # Attach session manager to request.state
        request.state.session = cast(_SessionManager, session_manager)
        
        # Process the request
        response = await call_next(request)
        
        return response
