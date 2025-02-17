from flask import Blueprint, Response, jsonify, request, current_app

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
    
    print(callback_result.callback_data)
    return jsonify({'test': 'test'}), 200
    
# @auth_route.route('/logout', methods=['GET', 'POST'])
# def logout():
#     service: AuthService = current_app.config["auth_service"]
#     resp = service.logout()
#     return resp
