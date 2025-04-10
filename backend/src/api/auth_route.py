import os
from typing import Any, Optional, List, Callable
import json
from fastapi import APIRouter, Request, HTTPException, status
from fastapi import Request
from fastapi.routing import APIRouter
from fastapi import FastAPI
from fastapi.responses import RedirectResponse, Response, JSONResponse
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware

from src.sdk.utils import debug_request, to_bool
from src.sdk.enums import CallbackResultType
from src.sdk.models import CallbackResult, LogoutConfig, SessionData
from src.sdk.auth_service import AuthService
from src.sdk.cookie_encryptor import CookieEncryptor
from src.api.auth_middleware import SessionAuthMiddleware

router = APIRouter()
app = FastAPI()

@app.middleware("http")
async def debug_request_middleware(request: Request, call_next):
    return await debug_request(request, call_next)

# Public paths that don't require authentication
PUBLIC_PATHS: List[str] = [
    "/api/auth/login",
    "/api/auth/callback",
    "/api/auth/logout",
    "/api/auth/test_decrypt_cookie"
]

# Add the session middleware to the app
app.add_middleware(SessionAuthMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@router.route('/session', methods=['GET', 'POST'])
def session(request: Request) -> Response | Any:
    session_secret_cookie: Optional[str] = os.getenv("SESSION_COOKIE_SECRET")
    if session_secret_cookie is None:
        raise ValueError("Missing required environment variable: SESSION_COOKIE_SECRET")

    # Get the session cookie
    session: Optional[str] = request.cookies.get("session")
    if session is None:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "No session found"}
        )

    try:
        # Decrypt the session cookie
        session_data_dict = CookieEncryptor(session_secret_cookie).decrypt(session)
        session_data = SessionData.from_dict(session_data_dict)
        
        # Check if we need to refresh the token
        auth_service: AuthService = request.app.state.auth_service
        if auth_service.is_expired(session_data.expires_at) and session_data.refresh_token:
            new_token_data = auth_service.refresh_token_if_expired(
                session_data.refresh_token, 
                session_data.expires_at
            )
            
            if new_token_data:
                # Update session with new token data
                session_data.access_token = new_token_data.access_token
                session_data.refresh_token = new_token_data.refresh_token
                session_data.expires_at = new_token_data.expires_at
                
                # Create a new response with updated session data
                response = JSONResponse(content=session_data.to_session_init_data())
                
                # Update the session cookie
                encrypted_session = CookieEncryptor(session_secret_cookie).encrypt(
                    session_data.to_dict()
                )
                
                secure: bool = not to_bool(os.getenv("DANGEROUSLY_DISABLE_SECURE_COOKIES", "False"))
                response.set_cookie(
                    key="session",
                    value=encrypted_session,
                    secure=secure,
                    httponly=True,
                    samesite="lax"
                )
                
                return response
        
        # Return the session data
        return JSONResponse(content=session_data.to_session_init_data())
    except Exception as e:
        print(f"Session endpoint error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": f"Session error: {str(e)}"}
        )

@router.route('/login', methods=['GET', 'POST'])
def login(request: Request) -> Response | Any:
    service: AuthService = request.app.state.auth_service    
    resp: Response = service.login(req=request)
    return resp

@router.route('/callback', methods=['GET', 'POST'])
def callback(request: Request) -> Response | Any:

    service: AuthService = request.app.state.auth_service
    callback_result: CallbackResult = service.callback(req=request)

    if callback_result.type == CallbackResultType.REDIRECT_REQUIRED and callback_result.redirect_response:
        return callback_result.redirect_response
    
    app_home_url: str | None = os.getenv("APP_HOME_URL")
    if app_home_url is None:
        raise ValueError("Missing required environment variable: APP_HOME_URL")
    

    resp: Response = service._create_callback_response(request, app_home_url)

    session_secret_cookie: Optional[str] = os.getenv("SESSION_COOKIE_SECRET")
    if session_secret_cookie is None:
        raise ValueError("Missing required environment variable: SESSION_COOKIE_SECRET")
    
    if callback_result.callback_data is None:
        raise ValueError("Missing callback data")

    secure: bool = not to_bool(os.getenv("DANGEROUSLY_DISABLE_SECURE_COOKIES", "False"))

    resp.set_cookie(
        key="session",
        value=CookieEncryptor(session_secret_cookie).encrypt(
            callback_result.callback_data.to_session()
        ),
        secure=secure,
        httponly=True,
        samesite="lax"
    )
    
    return resp

@router.route('/logout', methods=['GET', 'POST'])
def logout(request: Request) -> Response | Any:

    # Get environment variables
    session_secret_cookie: Optional[str] = os.getenv("SESSION_COOKIE_SECRET")
    if session_secret_cookie is None:
        raise ValueError("Missing required environment variable: SESSION_COOKIE_SECRET")
    
    secure: bool = not to_bool(os.getenv("DANGEROUSLY_DISABLE_SECURE_COOKIES", "False"))

    # Get the auth service from the current app
    service: AuthService = request.app.state.auth_service

    # Get the session from the request
    session: Optional[str] = request.cookies.get("session")
    if session is None:
        return "No session found", 400

    # Decrypt the session
    session_data: dict[str, Any] = CookieEncryptor(session_secret_cookie).decrypt(session)

    # Logout the user
    resp: Response = service.logout(
        req=request,
        config=LogoutConfig(
            refresh_token=session_data.get("refresh_token"),
            redirect_uri=os.getenv("REDIRECT_URI", ""), # up to developer to set
            tenant_custom_domain=session_data.get("tenant_custom_domain"),
            tenant_domain_name=session_data.get("tenant_domain_name")
        )
    )

    # Delete the session cookie
    resp.set_cookie(
        key="session",
        value='',
        secure=secure,
        httponly=True,
        samesite="lax",
        max_age=0
    )

    return resp


class TestDecryptCookieResponse(BaseModel):
    decrypted_cookie: dict[str, Any]

@router.get('/test_decrypt_cookie')
@router.post('/test_decrypt_cookie')
def test_decrypt_cookie(request: Request) -> TestDecryptCookieResponse:
    session_secret_cookie: Optional[str] = os.getenv("SESSION_COOKIE_SECRET")
    if session_secret_cookie is None:
        raise ValueError("Missing required environment variable: SESSION_COOKIE_SECRET")

    cookie_value: str | None = request.cookies.get("session")
    if cookie_value is None:
        return TestDecryptCookieResponse(decrypted_cookie={})

    decrypted_cookie = CookieEncryptor(session_secret_cookie).decrypt(cookie_value)
    print(f"Decrypted cookie: {decrypted_cookie}")
    
    return TestDecryptCookieResponse(decrypted_cookie=decrypted_cookie)
