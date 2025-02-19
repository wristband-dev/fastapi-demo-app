import os
from flask import Blueprint, Response, make_response, request, current_app

from src.sdk.enums import CallbackResultType
from src.sdk.models import CallbackResult
from src.sdk.auth_service import AuthService

auth_route = Blueprint('auth', __name__)

@auth_route.route('/login', methods=['GET', 'POST'])
def login():
    service: AuthService = current_app.config["auth_service"]
    resp: Response = service.login(req=request)
    return resp

@auth_route.route('/callback', methods=['GET', 'POST'])
def callback():
    service: AuthService = current_app.config["auth_service"]
    callback_result: CallbackResult = service.callback(req=request)
    
    if callback_result.type == CallbackResultType.REDIRECT_REQUIRED and callback_result.redirect_response:
        return callback_result.redirect_response
    
    app_home_url = os.getenv("APP_HOME_URL")
    if app_home_url is None:
        raise ValueError("Missing required environment variable: APP_HOME_URL")
    
    return service.create_callback_response(request, app_home_url)
    
# @auth_route.route('/logout', methods=['GET', 'POST'])
# def logout():
#     service: AuthService = current_app.config["auth_service"]
#     resp = service.logout()
#     return resp
