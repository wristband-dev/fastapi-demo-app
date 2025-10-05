import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status

from auth.wristband import require_session_auth
from models.schemas import NicknameResponse
from services.wristband_service import WristbandService
from utils.nicknames import generate_nickname


# WRISTBAND_TOUCHPOINT: Example of auth validation at the router level
router = APIRouter(dependencies=[Depends(require_session_auth)])
logger = logging.getLogger(__name__)
wristband_service = WristbandService()


@router.get("")
async def get_nickname(request: Request) -> NicknameResponse:
    try:
        # Get the Wristband user's existing nickname
        nickname: str = await wristband_service.get_user_nickname(
            user_id=request.state.session.user_id,
            access_token=request.state.session.access_token
        )
        return NicknameResponse(nickname=nickname)
    except Exception as e:
        logger.exception(f"Unexpected Get Nickname Endpoint error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("")
async def generate_new_nickname(request: Request) -> NicknameResponse:
    try:
        # Update the Wristband user with the new nickname
        nickname: str = generate_nickname()
        await wristband_service.update_user_nickname(
            user_id=request.state.session.user_id,
            nickname=nickname,
            access_token=request.state.session.access_token
        )
        return NicknameResponse(nickname=nickname)
    except Exception as e:
        logger.exception(f"Unexpected Generate New Nickname Endpoint error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
