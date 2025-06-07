# Standard library imports
from fastapi import APIRouter, Request
from fastapi import Request
from fastapi.routing import APIRouter
from fastapi.responses import Response
import logging

# Wristband imports
from wristband.enums import CallbackResultType
from wristband.models import CallbackResult, LogoutConfig, SessionData
from wristband.fastapi.auth import Auth
from wristband.utils import get_logger, create_csrf_token

# Local imports
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
    
    # create callback response
    resp: Response = auth._create_callback_response(request, "http://localhost:3001")

    #
    # TODO: SDK shouldn't be so rigid with callback_data to allow csrf_token to be added in here directly.
    #

    # Create CSRF token
    csrf_token = create_csrf_token()

    # Set a separate CSRF token cookie
    update_csrf_cookie(csrf_token, resp, False)
    
    # Set session cookie
    session_data = callback_result.callback_data.to_session()
    update_session_cookie(resp, session_data, False)

    # return response
    return resp

@router.get('/logout')
def logout(request: Request) -> Response:
    auth: Auth = request.app.state.auth

    # Get the user's session
    session_data: SessionData | None = get_session_data(request)
    
    refresh_token = session_data.refresh_token
    tenant_custom_domain = session_data.tenant_custom_domain
    tenant_domain_name = session_data.tenant_domain_name

    # Log out the user and redirect to the Wristband Logout Endpoint
    resp: Response = auth.logout(
        req=request,
        config=LogoutConfig(
            refresh_token=refresh_token,
            tenant_custom_domain=tenant_custom_domain,
            tenant_domain_name=tenant_domain_name,
            redirect_url="http://localhost:3001",
        )
    )

    # Delete the session and CSRF cookies.
    delete_session_cookie(resp, False)
    delete_csrf_cookie(resp, False)

    return resp
