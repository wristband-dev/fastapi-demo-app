import os
from typing import Any, Optional
from flask import Blueprint, Response, request, current_app

from src.sdk.utils import to_bool
from src.sdk.enums import CallbackResultType
from src.sdk.models import CallbackResult
from src.sdk.auth_service import AuthService
from src.sdk.cookie_encryptor import CookieEncryptor

auth_route = Blueprint('auth', __name__)

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
    
    resp: Response = service.create_callback_response(request, app_home_url)

    session_secret_cookie: Optional[str] = os.getenv("SESSION_COOKIE_SECRET")
    if session_secret_cookie is None:
        raise ValueError("Missing required environment variable: SESSION_COOKIE_SECRET")
    
    if callback_result.callback_data is None:
        raise ValueError("Missing callback data")

    secure: bool = not to_bool(os.getenv("DANGEROUSLY_DISABLE_SECURE_COOKIES", "False"))

    resp.set_cookie(
        key="session",
        value=CookieEncryptor(session_secret_cookie).encrypt(callback_result.callback_data.to_session()),
        secure=secure,
        httponly=True,
        samesite="lax"
    )

    for header, value in resp.headers:
        if header == 'Set-Cookie':
            print(f"Cookie: {value}")

    return resp

@auth_route.route('/test_decrypt_cookie', methods=['GET', 'POST'])
def test_decrypt_cookie() -> Response | Any:
    session_secret_cookie: Optional[str] = os.getenv("SESSION_COOKIE_SECRET")
    if session_secret_cookie is None:
        raise ValueError("Missing required environment variable: SESSION_COOKIE_SECRET")

    cookie_value = request.cookies.get("session")
    if cookie_value is None:
        return "No cookie found", 400

    decrypted_cookie = CookieEncryptor(session_secret_cookie).decrypt(cookie_value)
    print(f"Decrypted cookie: {decrypted_cookie}")
    
    return decrypted_cookie
    
# @auth_route.route('/logout', methods=['GET', 'POST'])
# def logout():
#     service: AuthService = current_app.config["auth_service"]
#     resp = service.logout()
#     return resp
