from flask import Blueprint, Response, jsonify, request, current_app

from src.service.auth_service import AuthService

auth_route = Blueprint('auth', __name__)

@auth_route.route('/login', methods=['GET', 'POST'])
def login():
    service: AuthService = current_app.config["auth_service"]
    resp: Response = service.login(req=request)
    return resp

# @auth_route.route('/logout', methods=['GET', 'POST'])
# def logout():
#     service: AuthService = current_app.config["auth_service"]
#     resp = service.logout()
#     return resp
