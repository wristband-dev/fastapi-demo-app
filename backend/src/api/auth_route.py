from urllib import response
from flask import Blueprint, jsonify, request
import logging

from src.service.auth_service import AuthService

logger = logging.getLogger(__name__)

auth_route = Blueprint('auth', __name__)

@auth_route.route('/login', methods=['GET', 'POST'])
def login():
    """
    1. Instantiate AuthService with the current request (Flask's `request`).
    2. Get back a redirect response that has cookies set.
    3. Return that response.
    """
    logger.debug(f"Request path: {request.path}")
    
    service = AuthService(req=request)
    resp = service.login()  # resp is a Flask Response object w/ a 302 redirect & cookies
    return resp

@auth_route.route('/logout', methods=['GET', 'POST'])
def logout():
    """
    1. Instantiate AuthService with the current request.
    2. Clear cookies and redirect the user to home (or wherever you want).
    """
    logger.debug(f"Request path: {request.path}")

    service = AuthService(req=request)
    resp = service.logout()  # Clears cookies & 302 redirect
    return resp
