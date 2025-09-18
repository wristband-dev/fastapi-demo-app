from fastapi import APIRouter, Request, Response
from wristband.fastapi_auth import CallbackData, CallbackResult, CallbackResultType, LogoutConfig

from auth.wristband import wristband_auth
from models.schemas import SessionData
from utils.csrf import create_csrf_token, delete_csrf_cookie, update_csrf_cookie

router = APIRouter()


@router.get("/login")
async def login(request: Request) -> Response:
    # Construct the authorize request URL and redirect to the Wristband Authorize Endpoint
    return await wristband_auth.login(req=request)


@router.get("/callback")
async def callback(request: Request) -> Response:
    # get callback result
    callback_result: CallbackResult = await wristband_auth.callback(req=request)

    # if redirect required, return redirect response
    if callback_result.type == CallbackResultType.REDIRECT_REQUIRED:
        return await wristband_auth.create_callback_response(request, callback_result.redirect_url)  # type: ignore

    # Create session data for the authenticated user, including CSRF token
    callback_data: CallbackData = callback_result.callback_data  # type: ignore
    session_data: SessionData = SessionData(
        is_authenticated=True,
        access_token=callback_data.access_token,
        expires_at=callback_data.expires_at,
        refresh_token=callback_data.refresh_token or None,
        user_id=callback_data.user_info["sub"],
        tenant_id=callback_data.user_info["tnt_id"],
        idp_name=callback_data.user_info["idp_name"],
        tenant_domain_name=callback_data.tenant_domain_name,
        tenant_custom_domain=callback_data.tenant_custom_domain or None,
        csrf_token=create_csrf_token(),  # CSRF_TOUCHPOINT
    )

    # Create the callback response that sets the session and CSRF cookies.
    response: Response = await wristband_auth.create_callback_response(request, "http://localhost:6001/home")
    request.state.session.update(response, session_data)
    update_csrf_cookie(response, session_data.csrf_token)  # CSRF_TOUCHPOINT
    return response


@router.get("/logout")
async def logout(request: Request) -> Response:
    session_data: SessionData = request.state.session.get()

    # Log out the user and redirect to the Wristband Logout Endpoint
    response: Response = await wristband_auth.logout(
        req=request,
        config=LogoutConfig(
            refresh_token=session_data.refresh_token if session_data else None,
            tenant_custom_domain=session_data.tenant_custom_domain if session_data else None,
            tenant_domain_name=session_data.tenant_domain_name if session_data else None,
        ),
    )

    # Delete the session and CSRF cookies.
    request.state.session.delete(response)
    delete_csrf_cookie(response)
    return response
