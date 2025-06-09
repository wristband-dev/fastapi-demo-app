# Standard imports
from fastapi import Request, Response
import ast
import logging

# Wristband imports
from wristband.utils import CookieEncryptor, get_logger

# Local imports
from models.session_data import SessionData

session_cookie_secret = "a8f5f167f44f4964e6c998dee827110c"

logger: logging.Logger = get_logger()

def get_session_data(request: Request) -> SessionData | None:
    session_cookie = request.cookies.get("session")
    if not session_cookie:
        logger.warning(f"No session cookie found for request to {request.url.path}")
        return None

    try:
        # Decrypt the session cookie
        logger.debug("Attempting to decrypt session cookie")
        session_data_dict = CookieEncryptor(session_cookie_secret).decrypt(session_cookie)

        # Fix user_info if it's a string representation of a dict
        if 'user_info' in session_data_dict and isinstance(session_data_dict['user_info'], str):
            session_data_dict['user_info'] = ast.literal_eval(session_data_dict['user_info'])

        logger.debug("Session cookie decrypted successfully")
        return SessionData.from_dict(session_data_dict)
    except Exception as e:
        logger.error(f"Failed to decrypt session cookie: {str(e)}")
        raise ValueError("Unable to decrypt session cookie")

def update_session_cookie(response: Response, session_data: SessionData, secure: bool) -> None:
    encrypted_session: str = CookieEncryptor(session_cookie_secret).encrypt(session_data.to_dict())
    response.set_cookie(
        key="session",
        value=encrypted_session,
        max_age=1800,
        secure=secure,
        httponly=True,
        samesite="lax"
    )

def delete_session_cookie(response: Response, secure: bool) -> None:
    response.set_cookie("session", value='', max_age=0, secure=secure, httponly=True, samesite="lax")
