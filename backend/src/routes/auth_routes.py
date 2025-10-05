import logging
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from wristband.fastapi_auth import CallbackResult, CallbackResultType, LogoutConfig, SessionResponse, TokenResponse

from auth.wristband import require_session_auth, wristband_auth

router = APIRouter()
logger = logging.getLogger(__name__)


# WRISTBAND_TOUCHPOINT: Login Endpoint
@router.get("/login")
async def login(request: Request) -> Response:
    # Construct the authorize request URL and redirect to the Wristband Authorize Endpoint
    return await wristband_auth.login(request)


# WRISTBAND_TOUCHPOINT: Callback Endpoint
@router.get("/callback")
async def callback(request: Request) -> Response:
    # Get callback result
    callback_result: CallbackResult = await wristband_auth.callback(request)

    # If redirect required, return redirect response
    if callback_result.type == CallbackResultType.REDIRECT_REQUIRED:
        return await wristband_auth.create_callback_response(request, callback_result.redirect_url)  # type: ignore

    # Create a session for the authenticated user.
    request.state.session.from_callback(callback_result.callback_data)

    # Return the callback response that redirects to your app.
    return await wristband_auth.create_callback_response(request, "http://localhost:6001/home")


# WRISTBAND_TOUCHPOINT: Logout Endpoint
@router.get("/logout")
async def logout(request: Request) -> Response:
    # Log out the user and redirect to the Wristband Logout Endpoint
    response: Response = await wristband_auth.logout(
        request=request,
        config=LogoutConfig(
            refresh_token=request.state.session.refresh_token,
            tenant_custom_domain=request.state.session.tenant_custom_domain,
            tenant_name=request.state.session.tenant_name,
        ),
    )

    # Delete the session and CSRF cookies.
    request.state.session.clear()
    return response


# WRISTBAND_TOUCHPOINT: Check auth for this protected route
@router.get("/session", dependencies=[Depends(require_session_auth)])
async def get_session(request: Request) -> SessionResponse:
    try:
        return request.state.session.get_session_response(metadata={
            "isAuthenticated": request.state.session.is_authenticated,
            "accessToken": request.state.session.access_token,
            "expiresAt": request.state.session.expires_at,
            "userId": request.state.session.user_id,
            "tenantId": request.state.session.tenant_id,
            "tenantName": request.state.session.tenant_name,
            "csrfToken": request.state.session.csrf_token,
            "refreshToken": request.state.session.refresh_token,
        })
    except Exception as e:
        logger.exception(f"Unexpected Get Session Endpoint error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# WRISTBAND_TOUCHPOINT: Check auth for this protected route
@router.get("/token", dependencies=[Depends(require_session_auth)])
async def get_token(request: Request) -> TokenResponse:
    try:
        return request.state.session.get_token_response()
    except Exception as e:
        logger.exception(f"Unexpected Get Token Endpoint error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
