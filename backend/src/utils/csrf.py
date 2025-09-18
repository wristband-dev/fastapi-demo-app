import secrets

from fastapi.responses import Response

# IMPORTANT: Set this to True in Production!!!
is_csrf_cookie_secure = False


# CSRF_TOUCHPOINT
def create_csrf_token() -> str:
    return secrets.token_hex(32)


def update_csrf_cookie(response: Response, csrf_token: str) -> None:
    if not csrf_token:
        raise ValueError("[csrf_token] cannot be None")

    response.set_cookie(
        key="CSRF-TOKEN",
        value=csrf_token,
        httponly=False,  # Must be False so frontend JavaScript can access the value
        max_age=1800,  # 30 minutes in seconds
        path="/",
        samesite="lax",  # Equivalent to sameSite: true in JS
        secure=is_csrf_cookie_secure,  # IMPORTANT: Set this to True in Production!!!
    )


def delete_csrf_cookie(response: Response) -> None:
    response.set_cookie(
        "CSRF-TOKEN",
        value="",
        max_age=0,
        httponly=False,
        samesite="lax",
        secure=is_csrf_cookie_secure,  # IMPORTANT: Set this to True in Production!!!
    )
