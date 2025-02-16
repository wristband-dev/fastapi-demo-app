import base64
import os
import secrets
import time
import json
from typing import Optional
from urllib.parse import urlencode
import hashlib
from flask import Request, Response, make_response
from cryptography.fernet import Fernet

from src.models.auth import AuthConfig
from src.models.login import LoginConfig, LoginState


class AuthService:
    """
    static values shared by all instances of classes
    """
    _cookie_prefix = 'login#'
    _login_state_cookie_separator = '-'

    def __init__(self, auth_config: AuthConfig):
        """
        dynamic values of auth config
        """
        self.client_id = auth_config.client_id
        self.client_secret = auth_config.client_secret
        self.login_state_secret = auth_config.login_state_secret
        self.login_url = auth_config.login_url
        self.redirect_uri = auth_config.redirect_uri
        self.wristband_application_domain = auth_config.wristband_application_domain
        self.custom_application_login_page_url = auth_config.custom_application_login_page_url
        self.dangerously_disable_secure_cookies = auth_config.dangerously_disable_secure_cookies
        self.root_domain = auth_config.root_domain 
        self.scopes = auth_config.scopes
        self.use_custom_domains = auth_config.use_custom_domains
        self.use_tenant_subdomains = auth_config.use_tenant_subdomains
        # TODO - validation on auth config fields


    def login(
        self,
        req: Request,
        config: LoginConfig = LoginConfig()
    ) -> Response:
        """
        Initiates the login process by redirecting the user to the OAuth2 authorization endpoint.

        Args:
            req (Request): The Flask request object.
            config (LoginConfig, optional): Configuration for the login process. Defaults to LoginConfig().

        Returns:
            Response: The Flask response object with the appropriate redirection headers set.
        """
        res = make_response()

        res.headers['Cache-Control'] = 'no-store'
        res.headers['Pragma'] = 'no-cache'

        # Determine which domain-related values are present as it will be needed for the authorize URL.
        tenant_custom_domain: str  = self._resolve_tenant_custom_domain_param(req)
        tenant_domain_name: str = self._resolve_tenant_domain_name(req, self.root_domain)
        default_tenant_custom_domain: Optional[str] = config.default_tenant_custom_domain
        default_tenant_domain_name: Optional[str] = config.default_tenant_domain

        # In the event we cannot determine either a tenant custom domain or subdomain, send the user to app-level login.
        if not any([
            tenant_custom_domain,
            tenant_domain_name,
            default_tenant_custom_domain,
            default_tenant_domain_name
        ]):
            applogin_url = self.custom_application_login_page_url or f'https://{self.wristband_application_domain}/login'
            res.status_code = 302
            res.headers['Location'] = applogin_url
            return res

        # Create the login state which will be cached in a cookie so that it can be accessed in the callback.
        login_state: LoginState = self._create_login_state(req, self.redirect_uri, config.custom_state)

        # Clear any stale login state cookies and add a new one fo rthe current request.
        self._clear_oldest_login_state_cookie(req, res)
        encrypted_login_state: bytes = self._encrypt_login_state(login_state, self.login_state_secret)
        self._create_login_state_cookie(res, login_state.state, encrypted_login_state, self.dangerously_disable_secure_cookies)

        # Create the Wristband Authorize Endpoint URL which the user will get redirectd to.
        authorize_url: str = self._get_oauth_authorize_url(req, login_state, tenant_custom_domain, tenant_domain_name, default_tenant_custom_domain, default_tenant_domain_name)

        # Perform the redirect to Wristband's Authorize Endpoint.
        res.status_code = 302
        res.headers['Location'] = authorize_url
        return res

    # def callback(self, req: Request) -> Response:
    #     res = make_response()

    #     res.headers['Cache-Control'] = 'no-store'
    #     res.headers['Pragma'] = 'no-cache'


    # --------- Login State Cookie Management --------- #
    def _resolve_tenant_custom_domain_param(self, req: Request) -> str:
        tenant_custom_domain = req.args.get('tenant_custom_domain')
        if tenant_custom_domain and not isinstance(tenant_custom_domain, str):
            raise TypeError('More than one [tenant_custom_domain] query parameter was encountered')
        return tenant_custom_domain or ''
    
    def _resolve_tenant_domain_name(self, req: Request, root_domain: Optional[str]) -> str:

        def parse_tenant_subdomain(req: Request, root_domain: Optional[str]) -> Optional[str]:
            host = req.host
            if root_domain is None or not host.endswith(root_domain):
                return None

            subdomain = host[:-len(root_domain)].rstrip('.')
            if subdomain:
                return subdomain

            return None
        
        if self.use_tenant_subdomains:
            return parse_tenant_subdomain(req, root_domain) or ''

        tenant_domain_param = req.args.get('tenant_domain')
        if tenant_domain_param and not isinstance(tenant_domain_param, str):
            raise TypeError('More than one [tenant_domain] query parameter was encountered')

        return tenant_domain_param or ''

    def _create_login_state(self, req: Request, redirect_uri: str, custom_state: Optional[dict[str, str]]) -> LoginState:

        return_url = req.args.get('return_url')
        if isinstance(return_url, list):
            raise TypeError('More than one [return_url] query parameter was encountered')

        return LoginState(
            state=self._generate_random_string(32),
            code_verifier=self._generate_random_string(32),
            redirect_uri=redirect_uri,
            return_url=return_url if return_url else None,
            custom_state=custom_state
        )
    
    def _generate_random_string(self, length: int) -> str:
        random_bytes = secrets.token_bytes(length)
        random_string = base64.urlsafe_b64encode(random_bytes).decode('utf-8')
        return random_string.rstrip('=')[:length]

    def _clear_oldest_login_state_cookie(self, req: Request, res: Response):
        if not req.cookies:
            return

        login_cookie_names = [name for name in req.cookies if name.startswith(self._cookie_prefix)]
        if len(login_cookie_names) >= 3:
            timestamps = [name.split(self._login_state_cookie_separator)[2] for name in login_cookie_names]
            newest_timestamps = sorted(timestamps, reverse=True)[:2]
            for cookie_name in login_cookie_names:
                timestamp = cookie_name.split(self._login_state_cookie_separator)[2]
                if timestamp not in newest_timestamps:
                    res.delete_cookie(cookie_name)

    def _encrypt_login_state(self, login_state: LoginState, login_state_secret: str) -> bytes:
        key = base64.urlsafe_b64encode(login_state_secret.encode().ljust(32)[:32])
        f = Fernet(key)  # Must be a 32-byte URL-safe key
        encrypted = f.encrypt(json.dumps(login_state.to_dict()).encode('utf-8'))
        if len(encrypted) > 4096:
            raise TypeError('Login state cookie exceeds 4kB in size.')
        return encrypted
    
    def _create_login_state_cookie(self, res: Response, state: str, encrypted_login_state: bytes, disable_secure: bool = False):
        encrypted_str = encrypted_login_state.decode('utf-8')
        cookie_name = f"{self._cookie_prefix}{state}{self._login_state_cookie_separator}{str(time.time())}"
        res.set_cookie(
            cookie_name,
            encrypted_str,
            max_age=3600,
            secure=not disable_secure,
            httponly=True
        )

    def _get_oauth_authorize_url(self, req: Request, login_state: LoginState, tenant_custom_domain: str, tenant_domain_name: str, default_tenant_custom_domain: Optional[str], default_tenant_domain_name: Optional[str]) -> str:

        def base64_url_encode(data: bytes) -> str:
            b64 = base64.b64encode(data).decode()
            return b64.replace('+', '-').replace('/', '_').replace('=', '')
        

        login_hint = req.args.get('login_hint')

        if isinstance(login_hint, list):
            raise TypeError('More than one [login_hint] query parameter was encountered')

        query_params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'state': login_state.state,
            'scope': ' '.join(self.scopes),
            'code_challenge': base64_url_encode(
                hashlib.sha256(login_state.code_verifier.encode()).digest()
            ),
            'code_challenge_method': 'S256',
            'nonce': self._generate_random_string(32)
        }
        if login_hint:
            query_params['login_hint'] = login_hint

        separator = '.' if self.use_custom_domains else '-'

        if tenant_custom_domain:
            return f"https://{tenant_custom_domain}/api/v1/oauth2/authorize?{urlencode(query_params)}"
        elif tenant_domain_name:
            return f"https://{tenant_domain_name}{separator}{self.wristband_application_domain}/api/v1/oauth2/authorize?{urlencode(query_params)}"
        elif default_tenant_custom_domain:
            return f"https://{default_tenant_custom_domain}/api/v1/oauth2/authorize?{urlencode(query_params)}"
        else:
            return f"https://{default_tenant_domain_name}{separator}{self.wristband_application_domain}/api/v1/oauth2/authorize?{urlencode(query_params)}"