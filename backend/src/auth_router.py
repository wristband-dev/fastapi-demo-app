# Standard library imports
import os
from typing import Any, Optional
import logging
from fastapi import APIRouter, Request, status
from fastapi import Request
from fastapi.routing import APIRouter
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel

# Wristband imports
from wristband.enums import CallbackResultType
from wristband.models import CallbackResult, LogoutConfig, SessionData
from wristband.fastapi.auth import Auth
from wristband.utils import CookieEncryptor, get_logger, to_bool

from src.config_utils import get_config_value

# Configure logger
logger: logging.Logger = get_logger()

# Initialize router
router = APIRouter()

# TODO - clean up session logic (401 on no session)
@router.route('/session', methods=['GET', 'POST'])
def session(request: Request) -> Response | Any:
    logger.debug("Session endpoint called")

    session_secret_cookie: Optional[str] = get_config_value("secrets", "session_cookie_secret")
    if session_secret_cookie is None:
        logger.error("Missing required environment variable: SESSION_COOKIE_SECRET")
        raise ValueError("Missing required environment variable: SESSION_COOKIE_SECRET")

    # Get the session cookie
    session: Optional[str] = request.cookies.get("session")
    if session is None:
        logger.warning("No session cookie found in request")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "No session found"}
        )

    try:
        # Decrypt the session cookie
        logger.debug("Attempting to decrypt session cookie")
        session_data_dict = CookieEncryptor(session_secret_cookie).decrypt(session)
        session_data = SessionData.from_dict(session_data_dict)

        logger.debug("Session cookie decrypted successfully")
        
        # Check if we need to refresh the token
        auth: Auth = request.app.state.auth
        if auth.is_expired(session_data.expires_at) and session_data.refresh_token:
            logger.info("Token is expired, attempting to refresh")
            new_token_data = auth.refresh_token_if_expired(
                session_data.refresh_token, 
                session_data.expires_at
            )
            
            if new_token_data:
                logger.info("Token refreshed successfully")
                # Update session with new token data
                session_data.access_token = new_token_data.access_token
                session_data.refresh_token = new_token_data.refresh_token
                session_data.expires_at = new_token_data.expires_at
                
                # Create a new response with updated session data
                response = JSONResponse(content=session_data.to_session_init_data())
                
                # Update the session cookie
                encrypted_session: str = CookieEncryptor(session_secret_cookie).encrypt(
                    session_data.to_dict()
                )
                
                secure: bool = not to_bool(get_config_value("wristband", "dangerously_disable_secure_cookies"))
                response.set_cookie(
                    key="session",
                    value=encrypted_session,
                    secure=secure,
                    httponly=True,
                    samesite="lax"
                )
                logger.debug("Updated session cookie with refreshed token")
                
                
                return response
            else:
                logger.warning("Token refresh failed")
        
        # Return the session data
        logger.debug("Returning session data to client")
        return JSONResponse(content=session_data.to_session_init_data())
    except Exception as e:
        logger.exception(f"Session endpoint error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": f"Session error: {str(e)}"}
        )

@router.route('/login', methods=['GET', 'POST'])
def login(request: Request) -> Response | Any:

    # init auth service
    auth: Auth = request.app.state.auth    

    # get login response
    resp: Response = auth.login(req=request)

    # return response
    return resp

@router.route('/callback', methods=['GET', 'POST'])
def callback(request: Request) -> Response | Any:

    # init auth service
    auth: Auth = request.app.state.auth

    # get callback result
    callback_result: CallbackResult = auth.callback(req=request)

    # if redirect required, return redirect response
    if callback_result.type == CallbackResultType.REDIRECT_REQUIRED and callback_result.redirect_response:
        return callback_result.redirect_response
    
    # get app home url
    app_host: str | None = get_config_value("app", "host")
    front_end_port: int | None = int(get_config_value("frontend", "port"))
    if app_host is None or front_end_port is None:
        raise ValueError("Missing required environment variable: APP_HOME_URL")
    app_home_url: str = f"{app_host}:{front_end_port}"
    
    # create callback response
    resp: Response = auth._create_callback_response(request, app_home_url)

    # get session secret cookie
    session_secret_cookie: Optional[str] = get_config_value("secrets", "session_cookie_secret")
    if session_secret_cookie is None:
        raise ValueError("Missing required environment variable: SESSION_COOKIE_SECRET")
    
    # if callback data is missing, raise error
    if callback_result.callback_data is None:
        raise ValueError("Missing callback data")

    # get secure flag
    secure: bool = not to_bool(get_config_value("wristband", "dangerously_disable_secure_cookies"))

    # set session cookie
    resp.set_cookie(
        key="session",
        value=CookieEncryptor(session_secret_cookie).encrypt(
            callback_result.callback_data.to_session()
        ),
        secure=secure,
        httponly=True,
        samesite="lax"
    )

    # return response
    return resp

@router.route('/logout', methods=['GET', 'POST'])
def logout(request: Request) -> Response | Any:

    # Get environment variables
    session_secret_cookie: Optional[str] = get_config_value("secrets", "session_cookie_secret")
    if session_secret_cookie is None:
        raise ValueError("Missing required environment variable: SESSION_COOKIE_SECRET")
    
    secure: bool = not to_bool(get_config_value("wristband", "dangerously_disable_secure_cookies"))

    # Get the auth service from the current app
    auth: Auth = request.app.state.auth

    # Get the session from the request
    session: Optional[str] = request.cookies.get("session")
    if session is None:
        return "No session found", 400

    # Decrypt the session
    session_data: dict[str, Any] = CookieEncryptor(session_secret_cookie).decrypt(session)

    app_host: str | None = get_config_value("app", "host")
    front_end_port: int | None = int(get_config_value("frontend", "port"))
    if app_host is None or front_end_port is None:
        raise ValueError("Missing required environment variable: APP_HOME_URL")
    app_home_url: str = f"{app_host}:{front_end_port}"

    # Logout the user
    resp: Response = auth.logout(
        req=request,
        config=LogoutConfig(
            refresh_token=session_data.get("refresh_token"),
            redirect_url=app_home_url,
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
    session_secret_cookie: Optional[str] = get_config_value("secrets", "session_cookie_secret")

    cookie_value: str | None = request.cookies.get("session")
    if cookie_value is None:
        return TestDecryptCookieResponse(decrypted_cookie={})

    decrypted_cookie = CookieEncryptor(session_secret_cookie).decrypt(cookie_value)
    
    return TestDecryptCookieResponse(decrypted_cookie=decrypted_cookie)
