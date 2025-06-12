# Standard imports
from fastapi import Request, Response
import logging

# Wristband imports
from wristband.utils import CookieEncryptor

# Local imports
from models.session_data import SessionData

logger = logging.getLogger(__name__)
cookie_encryptor = CookieEncryptor("dummy167f44f4964e6c998dee827110c")

def get_session_data(request: Request) -> SessionData:
    session_cookie = request.cookies.get("session")
    if not session_cookie:
        return SessionData.empty()

    try:
        session_data_dict = cookie_encryptor.decrypt(session_cookie)
        return SessionData.from_dict(session_data_dict)
    except Exception as e:
        logger.error(f"Failed to decrypt session cookie: {str(e)}")
        raise ValueError("Unable to decrypt session cookie")

def update_session_cookie(response: Response, session_data: SessionData) -> None:
    response.set_cookie(
        key="session",
        value=cookie_encryptor.encrypt(session_data.to_dict()),
        max_age=1800,
        secure=False,  # IMPORTANT: Set secure=True in Production!!!
        httponly=True,
        samesite="lax"
    )

def delete_session_cookie(response: Response) -> None:
     # IMPORTANT: Set secure=True in Production!!!
    response.set_cookie("session", value='', max_age=0, secure=False, httponly=True, samesite="lax")
