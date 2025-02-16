import base64
from typing import Any
import requests

from src.sdk.models import TokenResponse


class WristbandService:
    def __init__(self, wristband_application_domain: str, client_id: str, client_secret: str) -> None:
        credentials = f"{client_id}:{client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        
        self.base_url = f'https://{wristband_application_domain}/api/v1'
        self.headers = { 
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

    def get_tokens(self, code: str, redirect_uri: str, code_verifier: str) -> TokenResponse:
        form_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'code_verifier': code_verifier,
        }

        response = requests.post(
            self.base_url + '/oauth2/token', 
            data=form_data,
            headers=self.headers
        )

        return TokenResponse.from_api_response(response.json())


    def get_userinfo(self, access_token: str) -> dict[str, Any]:

        response = requests.get(
            self.base_url + '/oauth2/userinfo',
            headers={ 'Authorization': f'Bearer {access_token}' }
        )

        return response.json()