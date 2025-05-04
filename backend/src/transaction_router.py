# Standard library imports
import logging
from typing import Any
from fastapi import APIRouter, Request, Response

# Wristband imports
from wristband.utils import get_logger

# Configure logger
logger: logging.Logger = get_logger()

# Initialize router
router = APIRouter()


@router.route('/', methods=['POST'])
def transaction(request: Request) -> Response | Any:
    logger.debug("Transaction endpoint called")

    return Response(status_code=200)