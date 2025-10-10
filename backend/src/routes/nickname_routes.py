import logging
from fastapi import APIRouter, Depends, HTTPException, status
from wristband.fastapi_auth import get_session

from auth.wristband import require_session_auth
from models.schemas import MySession, NicknameResponse
from services.wristband_service import WristbandService
from utils.nicknames import generate_nickname

# WRISTBAND_TOUCHPOINT: Route-level auth validations
router = APIRouter(dependencies=[Depends(require_session_auth)])
logger = logging.getLogger(__name__)
wristband_service = WristbandService()


@router.get("")
async def get_nickname(session: MySession = Depends(get_session)) -> NicknameResponse:
    """
    Get the Wristband user's existing nickname
    """
    try:
        assert session.user_id is not None
        assert session.access_token is not None
        nickname: str = await wristband_service.get_user_nickname(session.user_id, session.access_token)
        return NicknameResponse(nickname=nickname)
    except Exception as e:
        logger.exception(f"Unexpected Get Nickname Endpoint error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("")
async def generate_new_nickname(session: MySession = Depends(get_session)) -> NicknameResponse:
    """
    Update the Wristband user with the new nickname
    """
    try:
        assert session.user_id is not None
        assert session.access_token is not None
        nickname: str = generate_nickname()
        await wristband_service.update_user_nickname(session.user_id, nickname, session.access_token)
        return NicknameResponse(nickname=nickname)
    except Exception as e:
        logger.exception(f"Unexpected Generate New Nickname Endpoint error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
