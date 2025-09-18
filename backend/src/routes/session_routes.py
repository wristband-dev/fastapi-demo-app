import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status

from auth.session_auth_dependencies import require_session_auth
from models.schemas import SessionData, SessionResponse

router = APIRouter()
logger = logging.getLogger(__name__)


# WRISTBAND_TOUCHPOINT: Check auth for this protected route
@router.get("", dependencies=[Depends(require_session_auth)], response_model=SessionResponse)
async def get_session(request: Request) -> SessionResponse:
    try:
        session_data: SessionData = request.state.session.get()
        return SessionResponse(
            tenant_id=session_data.tenant_id,
            user_id=session_data.user_id,
            metadata=session_data,
        )
    except Exception as e:
        logger.exception(f"Unexpected Get Session Endpoint error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
