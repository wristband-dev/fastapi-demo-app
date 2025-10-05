import json
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, status
from wristband.python_jwt import JWTPayload

from auth.jwt_auth_dependencies import require_jwt_auth
from models.schemas import HelloWorldResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("")
async def say_hello(request: Request, jwt_payload: JWTPayload = Depends(require_jwt_auth)) -> HelloWorldResponse:
    try:
        # If needed, you can access the contents of the JWT payload in your routes.
        logger.info(f"Successful JWT validation for user: {getattr(jwt_payload, 'sub', 'unknown')}")

        body = await request.json()
        if "message" not in body or body["message"] != "Hello":
            raise HTTPException(status_code=400, detail="Request body 'message' field must equal 'Hello'")

        current_time = datetime.now().replace(microsecond=0).isoformat()
        return HelloWorldResponse(message=f'You said "Hello" at {current_time}')
    except HTTPException:
        raise  # We want to raise 4xx errors
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in request body")
    except Exception as e:
        logger.exception(f"Unexpected Hello World Endpoint error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
