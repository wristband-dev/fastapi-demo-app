# Standard library imports
from datetime import datetime, timedelta
from fastapi import APIRouter, Request
from fastapi import Request
from fastapi.routing import APIRouter
from fastapi.responses import Response

# Wristband imports
from wristband.models import CallbackResult, CallbackData, LogoutConfig, CallbackResultType

# Local imports
from auth.wristband import wristband_auth
from models.session_data import SessionData
from utils.csrf import create_csrf_token, delete_csrf_cookie, update_csrf_cookie
from utils.session import delete_session_cookie, update_session_cookie

router = APIRouter()


@router.get('/login')
def login(request: Request) -> Response:
    # Construct the authorize request URL and redirect to the Wristband Authorize Endpoint
    resp: Response = wristband_auth.login(req=request)
    return resp

@router.get('/callback')
def callback(request: Request) -> Response:
    # get callback result
    callback_result: CallbackResult = wristband_auth.callback(req=request)

    # if redirect required, return redirect response
    if callback_result.type == CallbackResultType.REDIRECT_REQUIRED and callback_result.redirect_response:
        return callback_result.redirect_response
    
    if not callback_result.callback_data:
        raise ValueError("Callback data unexpectedly set to None")

    # CSRF_TOUCHPOINT
    # Create CSRF token to store in both session and CSRF cookies
    csrf_token = create_csrf_token()
    
    # Create session data for the authenticated user
    callback_data: CallbackData = callback_result.callback_data
    session_data: SessionData = SessionData(
        is_authenticated=True,
        access_token=callback_data.access_token,
        # Convert the "expiresIn" seconds into milliseconds from the epoch.
        expires_at=int((datetime.now() + timedelta(seconds=callback_data.expires_in)).timestamp() * 1000),
        refresh_token=callback_data.refresh_token or None,
        user_id=callback_data.user_info['sub'],
        tenant_id=callback_data.user_info['tnt_id'],
        idp_name=callback_data.user_info['idp_name'],
        tenant_domain_name=callback_data.tenant_domain_name,
        tenant_custom_domain=callback_data.tenant_custom_domain or None,
        csrf_token=csrf_token,
    )

    # Create the callback response that sets the session and CSRF cookies.
    resp: Response = wristband_auth._create_callback_response(request, "http://localhost:3001")
    update_session_cookie(resp, session_data)
    update_csrf_cookie(resp, csrf_token)
    return resp

@router.get('/logout')
def logout(request: Request) -> Response:
    session_data: SessionData = request.state.session

    # Log out the user and redirect to the Wristband Logout Endpoint
    resp: Response = wristband_auth.logout(
        req=request,
        config=LogoutConfig(
            refresh_token=session_data.refresh_token if session_data else None,
            tenant_custom_domain=session_data.tenant_custom_domain if session_data else None,
            tenant_domain_name=session_data.tenant_domain_name if session_data else None,
        )
    )

    # Delete the session and CSRF cookies.
    delete_session_cookie(resp)
    delete_csrf_cookie(resp)

    return resp
