import json
import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("")
async def say_hello(request: Request) -> Response:
    try:
        # Ensure 'message' field exists and equals "Hello"
        body = await request.json()
        if "message" not in body:
            raise HTTPException(status_code=400, detail="Request body must contain 'message' field")
        if body["message"] != "Hello":
            raise HTTPException(status_code=400, detail="Request body 'message' field must equal 'Hello'")

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return JSONResponse(content={"message": f'You said "Hello" at {current_time}'})
    except HTTPException:
        raise
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in request body")
    except Exception as e:
        logger.exception(f"Unexpected Hello World Endpoint error: {str(e)}")
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
