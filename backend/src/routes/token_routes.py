import logging

from fastapi import APIRouter, Request, Response, status
from fastapi.responses import JSONResponse

from models.session_data import SessionData

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("")
async def get_token(request: Request) -> Response:
    try:
        session_data: SessionData = request.state.session.get()
        return JSONResponse(
            content={
                "accessToken": session_data.access_token,
                "expiresAt": session_data.expires_at,
            }
        )
    except Exception as e:
        logger.exception(f"Unexpected Get Token Endpoint error: {str(e)}")
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
