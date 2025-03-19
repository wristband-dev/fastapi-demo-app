import os
from typing import Any, Optional
from flask import Blueprint, Response, request, current_app
from requests import Session

from src.sdk.utils import to_bool
from src.sdk.enums import CallbackResultType
from src.sdk.models import CallbackResult, LogoutConfig, SessionData
from src.sdk.auth_service import AuthService
from src.sdk.cookie_encryptor import CookieEncryptor

auth_route = Blueprint('auth', __name__)

"""
1
call session endpoint on initial page load
    - next js page router app demo has this
"""

"""
2
https://blog.teclado.com/protecting-endpoints-in-flask-apps-by-requiring-login/

add middleware logic to check if the user is authenticated in the session
check if the access token exists
check if the access token is expired
if the refresh token exists, try to refresh the access token

ELSE throw 401

"""
def login_required(func):
    return func



@auth_route.route('/login', methods=['GET', 'POST'])
def login() -> Response | Any:
    service: AuthService = current_app.config["auth_service"]    
    resp: Response = service.login(req=request)
    return resp

@auth_route.route('/callback', methods=['GET', 'POST'])
def callback() -> Response | Any:
    service: AuthService = current_app.config["auth_service"]
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

@auth_route.route('/logout', methods=['GET', 'POST'])
def logout() -> Response | Any:

    # Get environment variables
    session_secret_cookie: Optional[str] = os.getenv("SESSION_COOKIE_SECRET")
    if session_secret_cookie is None:
        raise ValueError("Missing required environment variable: SESSION_COOKIE_SECRET")
    
    secure: bool = not to_bool(os.getenv("DANGEROUSLY_DISABLE_SECURE_COOKIES", "False"))

    # Get the auth service from the current app
    service: AuthService = current_app.config["auth_service"]

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

@auth_route.route('/session', methods=['GET', 'POST'])
def session() -> Response | Any:
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




@auth_route.route('/test_decrypt_cookie', methods=['GET', 'POST'])
def test_decrypt_cookie() -> Response | Any:
    session_secret_cookie: Optional[str] = os.getenv("SESSION_COOKIE_SECRET")
    if session_secret_cookie is None:
        raise ValueError("Missing required environment variable: SESSION_COOKIE_SECRET")

    cookie_value: str | None = request.cookies.get("session")
    if cookie_value is None:
        return "No cookie found", 400

    decrypted_cookie = CookieEncryptor(session_secret_cookie).decrypt(cookie_value)
    print(f"Decrypted cookie: {decrypted_cookie}")
    
    return decrypted_cookie
