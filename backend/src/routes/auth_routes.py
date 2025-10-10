import logging
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from wristband.fastapi_auth import (
  CallbackResult,
  CallbackResultType,
  get_session,
  LogoutConfig,
  SessionResponse,
  TokenResponse
)

from auth.wristband import require_session_auth, wristband_auth
from models.schemas import MySession

router = APIRouter()
logger = logging.getLogger(__name__)


# WRISTBAND_TOUCHPOINT: Login Endpoint
@router.get("/login")
async def login(request: Request) -> Response:
    # Construct the authorize request URL and redirect to the Wristband Authorize Endpoint
    return await wristband_auth.login(request)


# WRISTBAND_TOUCHPOINT: Callback Endpoint
@router.get("/callback")
async def callback(request: Request, session: MySession = Depends(get_session)) -> Response:
    # Get callback result
    callback_result: CallbackResult = await wristband_auth.callback(request)

    # If redirect required, return redirect response
    if callback_result.type == CallbackResultType.REDIRECT_REQUIRED:
        assert callback_result.redirect_url is not None
        return await wristband_auth.create_callback_response(request, callback_result.redirect_url)

    # Create a session for the authenticated user.
    assert callback_result.callback_data is not None
    session.from_callback(callback_data=callback_result.callback_data, custom_fields={ "custom_field": "example" })

    # Return the callback response that redirects to your app.
    return await wristband_auth.create_callback_response(request, "http://localhost:6001/home")


# WRISTBAND_TOUCHPOINT: Logout Endpoint
@router.get("/logout")
async def logout(request: Request, session: MySession = Depends(get_session)) -> Response:
    # Get all necessary session data needed to perform logout
    logout_config = LogoutConfig(
        refresh_token=session.refresh_token,
        tenant_custom_domain=session.tenant_custom_domain,
        tenant_name=session.tenant_name,
    )

    # Delete the session and CSRF cookies.
    session.clear()

    # Log out the user and redirect to the Wristband Logout Endpoint
    return await wristband_auth.logout(request, logout_config)


# WRISTBAND_TOUCHPOINT: Session Endpoint
@router.get("/session")
async def get_session_response(session: MySession = Depends(require_session_auth)) -> SessionResponse:
    try:
        print(f"{session}")
        return session.get_session_response(metadata={
            "isAuthenticated": session.is_authenticated,
            "accessToken": session.access_token,
            "expiresAt": session.expires_at,
            "tenantName": session.tenant_name,
            "identityProviderName": session.identity_provider_name,
            "csrfToken": session.csrf_token,
            "refreshToken": session.refresh_token,
            "customField": session.custom_field,
        })
    except Exception as e:
        logger.exception(f"Unexpected Get Session Endpoint error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# WRISTBAND_TOUCHPOINT: Token Endpoint
@router.get("/token")
async def get_token_response(session: MySession = Depends(require_session_auth)) -> TokenResponse:
    try:
        return session.get_token_response()
    except Exception as e:
        logger.exception(f"Unexpected Get Token Endpoint error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
