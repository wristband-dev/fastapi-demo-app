from fastapi.responses import Response

# Custom function to update CSRF cookie
def update_csrf_cookie(csrf_token: str, response: Response, secure: bool = True) -> None:
    """Updates the CSRF cookie with the provided CSRF token.
    
    Args:
        csrf_token: The CSRF token to set in the cookie
        response: The FastAPI response object for setting the cookie
        secure: Whether to set the secure flag on the cookie
    """
    if not csrf_token:
        raise ValueError('[csrf_token] cannot be None')
    
    response.set_cookie(
        key="CSRF-TOKEN",
        value=csrf_token,
        httponly=False,  # Must be False so frontend JavaScript can access the value
        max_age=1800,    # 30 minutes in seconds
        path="/",
        samesite="lax",  # Equivalent to sameSite: true in JS
        secure=secure
    )

def delete_csrf_cookie(response: Response, secure: bool) -> None:
    response.set_cookie("CSRF-TOKEN", value='', max_age=0, secure=secure, httponly=False, samesite="lax")
