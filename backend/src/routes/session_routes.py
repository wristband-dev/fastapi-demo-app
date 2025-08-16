import logging

from fastapi import APIRouter, Request, Response, status
from fastapi.responses import JSONResponse

from models.session_data import SessionData

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("")
async def get_session(request: Request) -> Response:
    try:
        session_data: SessionData = request.state.session.get()
        return JSONResponse(
            content={
                "tenantId": session_data.tenant_id,
                "userId": session_data.user_id,
                "metadata": session_data.to_dict(),
            }
        )
    except Exception as e:
        logger.exception(f"Unexpected Get Session Endpoint error: {str(e)}")
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
