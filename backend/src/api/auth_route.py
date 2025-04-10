import os
from typing import Any, Optional
from fastapi import APIRouter, Request
from fastapi import Request
from fastapi.routing import APIRouter
from fastapi import FastAPI
from fastapi.responses import RedirectResponse, Response
from pydantic import BaseModel

from src.sdk.utils import debug_request, to_bool
from src.sdk.enums import CallbackResultType
from src.sdk.models import CallbackResult, LogoutConfig, SessionData
from src.sdk.auth_service import AuthService
from src.sdk.cookie_encryptor import CookieEncryptor

router = APIRouter()
app = FastAPI()

@app.middleware("http")
async def debug_request_middleware(request: Request, call_next):
    return await debug_request(request, call_next)

"""
1
call session endpoint on initial page load
    - next js page router app demo has this
"""
def login_required(func):
    return func
"""
2
https://blog.teclado.com/protecting-endpoints-in-flask-apps-by-requiring-login/

add middleware logic to check if the user is authenticated in the session
check if the access token exists
check if the access token is expired
if the refresh token exists, try to refresh the access token

ELSE throw 401

"""



@router.route('/session', methods=['GET', 'POST'])
def session(request: Request) -> Response | Any:
    session_secret_cookie: Optional[str] = os.getenv("SESSION_COOKIE_SECRET")
    if session_secret_cookie is None:
        raise ValueError("Missing required environment variable: SESSION_COOKIE_SECRET")

    # Get the session cookie
    session: Optional[str] = request.cookies.get("session")
    if session is None:
        return "No session found", 401

    # Decrypt the session cookie
    session_data: SessionData = SessionData.from_dict(
        CookieEncryptor(session_secret_cookie).decrypt(session)
    )

    # Return the session data
    return session_data.to_session_init_data()

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
