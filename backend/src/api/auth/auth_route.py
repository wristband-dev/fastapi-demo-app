from urllib import response
from flask import Blueprint, jsonify, request

from src.service.auth_service import AuthService

auth_route = Blueprint('auth', __name__)

@auth_route.route('/login', methods=['GET', 'POST'])
def login():
    return AuthService(req=request, res=response).login()

