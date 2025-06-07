from fastapi import APIRouter, Request, Response, status
from fastapi.responses import JSONResponse

from wristband.models import SessionData
from wristband.utils import get_logger

from utils.session import get_session_data

router = APIRouter()
logger = get_logger()


@router.get('/session')
def session(request: Request) -> Response:
    logger.debug("Session endpoint called")

    try:
        # Return the user's session data
        session_data: SessionData | None = get_session_data(request)
        if not session_data:
            logger.error("No authenticated session found.")
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "No authenticated session found."})

        return JSONResponse(content=session_data.to_session_init_data())
    except Exception as e:
        logger.exception("Session endpoint error")
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": f"Session error: {str(e)}"})

@router.post('/test_decrypt_cookie')
def test_decrypt_cookie(request: Request) -> JSONResponse:
    session_data: SessionData | None = get_session_data(request)
    if not session_data:
        logger.error("No authenticated session found.")
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "No authenticated session found."})

    return JSONResponse(content=session_data)
