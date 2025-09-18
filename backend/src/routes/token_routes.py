import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status

from auth.session_auth_dependencies import require_session_auth
from models.schemas import SessionData, TokenResponse

router = APIRouter()
logger = logging.getLogger(__name__)


# WRISTBAND_TOUCHPOINT: Check auth for this protected route
@router.get("", dependencies=[Depends(require_session_auth)], response_model=TokenResponse)
async def get_token(request: Request) -> TokenResponse:
    try:
        session_data: SessionData = request.state.session.get()
        return TokenResponse(
            access_token=session_data.access_token,
            expires_at=session_data.expires_at,
        )
    except Exception as e:
        logger.exception(f"Unexpected Get Token Endpoint error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
