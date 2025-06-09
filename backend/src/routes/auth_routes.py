# Standard library imports
from fastapi import APIRouter, Request
from fastapi import Request
from fastapi.routing import APIRouter
from fastapi.responses import Response
import logging

# Wristband imports
from wristband.enums import CallbackResultType
from wristband.models import CallbackResult, LogoutConfig
from wristband.fastapi.auth import Auth
from wristband.utils import get_logger, create_csrf_token

# Local imports
from models.session_data import SessionData
from utils.csrf import delete_csrf_cookie, update_csrf_cookie
from utils.session import delete_session_cookie, get_session_data, update_session_cookie

logger: logging.Logger = get_logger()
router = APIRouter()


@router.get('/login')
def login(request: Request) -> Response:
    auth: Auth = request.app.state.auth

    # Construct the authorize request URL and redirect to the Wristband Authorize Endpoint
    resp: Response = auth.login(req=request)
    return resp

@router.get('/callback')
def callback(request: Request) -> Response:
    auth: Auth = request.app.state.auth

    # get callback result
    callback_result: CallbackResult = auth.callback(req=request)

    # if redirect required, return redirect response
    if callback_result.type == CallbackResultType.REDIRECT_REQUIRED and callback_result.redirect_response:
        return callback_result.redirect_response
    
    if not callback_result.callback_data:
        raise ValueError("Callback data unexpectedly set to None")
    
    # create callback response
    resp: Response = auth._create_callback_response(request, "http://localhost:3001")

    # CSRF_TOUCHPOINT
    # Create CSRF token to store in both session and CSRF cookies
    csrf_token = create_csrf_token()
    update_csrf_cookie(csrf_token, resp, False)
    
    # Set session cookie
    session_data: SessionData = SessionData.from_callback_result_data(callback_result.callback_data, csrf_token)
    update_session_cookie(resp, session_data, False)

    # return response
    return resp

@router.get('/logout')
def logout(request: Request) -> Response:
    auth: Auth = request.app.state.auth

    # Get the user's session
    session_data: SessionData | None = get_session_data(request)

    # Log out the user and redirect to the Wristband Logout Endpoint
    resp: Response = auth.logout(
        req=request,
        config=LogoutConfig(
            refresh_token=session_data.refresh_token if session_data else None,
            tenant_custom_domain=session_data.tenant_custom_domain if session_data else None,
            tenant_domain_name=session_data.tenant_domain_name if session_data else None,
            redirect_url="http://localhost:3001",
        )
    )

    # Delete the session and CSRF cookies.
    delete_session_cookie(resp, False)
    delete_csrf_cookie(resp, False)

    return resp
