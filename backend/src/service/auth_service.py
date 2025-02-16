import base64
import os
import secrets
import time
import json
from typing import Optional
from urllib.parse import urlencode

from flask import Request, Response, make_response
from cryptography.fernet import Fernet

from src.models.login import LoginConfig, LoginState


class AuthService:
    def __init__(
        self, 
        req: Request, 
        res: Optional[Response] = None, 
        config: Optional[LoginConfig] = None
    ):
        self.req = req
        # If no Response object was passed in, create one
        self.res = res if res else make_response()
        self.config = config
        self.cookie_prefix = 'login#'
        self.login_state_cookie_separator = '-'

        # Disable caching
        self._disable_caching()

        # Determine domain-related values
        self.tenant_custom_domain = self._resolve_tenant_domain(self.resolve_tenant_from_custom_domain)
        self.tenant_domain_name = self._resolve_tenant_domain(self.resolve_tenant_from_domain)
        self.default_tenant_custom_domain = self._get_default_domain('default_tenant_custom_domain')
        self.default_tenant_domain_name = self._get_default_domain('default_tenant_domain')

    def login(self) -> Response:
        # If no domain is determined, do a simple 302 redirect
        if not any([
            self.tenant_custom_domain,
            self.tenant_domain_name,
            self.default_tenant_custom_domain,
            self.default_tenant_domain_name
        ]):
            self.res.status_code = 302
            self.res.headers['Location'] = f'https://{os.environ.get("APPLICATION_VANITY_DOMAIN")}/login'
            return self.res

        # Create and manage login state
        self.login_state = self.create_login_state(
            redirect_uri='https://localhost:8080/api/auth/callback',
            config=self.config
        )
        self._manage_login_state_cookies()

        # Redirect to OAuth provider
        oauth_url = self.get_oauth_authorize_url()
        self.res.status_code = 302
        self.res.headers['Location'] = oauth_url
        return self.res

    def logout(self) -> Response:
        # Clear relevant cookies
        if self.req.cookies:
            for cookie_name in self.req.cookies:
                if cookie_name.startswith(self.cookie_prefix):
                    self.res.delete_cookie(cookie_name)

        # 302 redirect to home
        self.res.status_code = 302
        self.res.headers['Location'] = '/'
        return self.res

    def _disable_caching(self):
        self.res.headers['Cache-Control'] = 'no-store'
        self.res.headers['Pragma'] = 'no-cache'

    def _resolve_tenant_domain(self, resolve_method) -> str:
        return resolve_method()

    def _get_default_domain(self, domain_attr: str) -> str:
        return getattr(self.config, domain_attr, '') if self.config else ''

    def _manage_login_state_cookies(self):
        self.clear_oldest_login_state_cookie(self.req, self.res)
        encrypted_login_state = self.encrypt_login_state(
            self.login_state,
            '7ffdbecc-ab7d-4134-9307-2dfcc52f7475'
        )
        self.create_login_state_cookie(
            self.res,
            self.login_state.state,
            encrypted_login_state,
            True
        )

    def resolve_tenant_from_domain(self) -> str:
        tenant = self._parse_tenant_subdomain()
        if tenant:
            return tenant

        tenant_domain = self.req.args.get('tenant_domain')
        if isinstance(tenant_domain, list):
            raise TypeError('More than one [tenant_domain] query parameter was encountered')
        return tenant_domain or ''

    def resolve_tenant_from_custom_domain(self) -> str:
        host = self._get_host_without_port()
        return self.config.custom_state.get(host, '') if self.config and self.config.custom_state else ''

    def _get_host_without_port(self) -> str:
        host = self.req.host
        return host.split(':')[0] if ':' in host else host

    def create_login_state(self, redirect_uri: str, config: Optional[LoginConfig] = None) -> LoginState:
        return_url = self.req.args.get('return_url')
        if isinstance(return_url, list):
            raise TypeError('More than one [return_url] query parameter was encountered')

        return LoginState(
            state=self._generate_random_string(32),
            code_verifier=self._generate_random_string(32),
            redirect_uri=redirect_uri,
            return_url=return_url if return_url else None,
            custom_state=config.custom_state if config and config.custom_state else None
        )

    def clear_oldest_login_state_cookie(self, req: Request, res: Response):
        if not req.cookies:
            return

        login_cookie_names = [name for name in req.cookies if name.startswith(self.cookie_prefix)]
        if len(login_cookie_names) >= 3:
            timestamps = [name.split(self.login_state_cookie_separator)[2] for name in login_cookie_names]
            newest_timestamps = sorted(timestamps, reverse=True)[:2]
            for cookie_name in login_cookie_names:
                timestamp = cookie_name.split(self.login_state_cookie_separator)[2]
                if timestamp not in newest_timestamps:
                    res.delete_cookie(cookie_name)

    def encrypt_login_state(self, login_state: LoginState, login_state_secret: str) -> bytes:
        f = Fernet(login_state_secret.encode())  # Must be a 32-byte URL-safe key
        encrypted = f.encrypt(json.dumps(login_state.to_dict()).encode('utf-8'))
        if len(encrypted) > 4096:
            raise TypeError('Login state cookie exceeds 4kB in size.')
        return encrypted

    def create_login_state_cookie(self, res: Response, state: str, encrypted_login_state: bytes, disable_secure: bool = False):
        encrypted_str = encrypted_login_state.decode('utf-8')
        cookie_name = f"{self.cookie_prefix}{state}{self.login_state_cookie_separator}{str(time.time())}"
        res.set_cookie(
            cookie_name,
            encrypted_str,
            max_age=3600,
            secure=not disable_secure,
            httponly=True
        )

    def _parse_tenant_subdomain(self) -> str:
        if not self.config or not self.config.default_tenant_domain:
            return ''
        host = self._get_host_without_port()
        if host.endswith(self.config.default_tenant_domain):
            return host[:-len(self.config.default_tenant_domain) - 1]
        return ''

    def _generate_random_string(self, length: int) -> str:
        random_bytes = secrets.token_bytes(length)
        random_string = base64.urlsafe_b64encode(random_bytes).decode('utf-8')
        return random_string.rstrip('=')[:length]

    def get_oauth_authorize_url(self) -> str:
        import hashlib

        login_hint = self.req.args.get('login_hint')
        if isinstance(login_hint, list):
            raise TypeError('More than one [login_hint] query parameter was encountered')

        query_params = {
            'client_id': "6y53fp4tjreqje74seffvq4idy",
            'redirect_uri': 'https://localhost:8080/api/auth/callback',
            'response_type': 'code',
            'state': self.login_state.state,
            'scope': 'openid offline_access profile email roles',
            'code_challenge': self._base64_url_encode(
                hashlib.sha256(self.login_state.code_verifier.encode()).digest()
            ),
            'code_challenge_method': 'S256',
            'nonce': self._generate_random_string(32)
        }
        if login_hint:
            query_params['login_hint'] = login_hint

        separator = '.' if (self.config and self.config.tenant_custom_domain) else '-'

        if self.tenant_custom_domain:
            return f"https://{self.tenant_custom_domain}/api/v1/oauth2/authorize?{urlencode(query_params)}"
        elif self.tenant_domain_name:
            vanity = os.environ.get('APPLICATION_VANITY_DOMAIN', 'example.com')
            return f"https://{self.tenant_domain_name}{separator}{vanity}/api/v1/oauth2/authorize?{urlencode(query_params)}"
        elif self.default_tenant_custom_domain:
            return f"https://{self.default_tenant_custom_domain}/api/v1/oauth2/authorize?{urlencode(query_params)}"
        else:
            vanity = os.environ.get('APPLICATION_VANITY_DOMAIN', 'example.com')
            return f"https://{self.default_tenant_domain_name}{separator}{vanity}/api/v1/oauth2/authorize?{urlencode(query_params)}"

    def _base64_url_encode(self, data: bytes) -> str:
        b64 = base64.b64encode(data).decode()
        return b64.replace('+', '-').replace('/', '_').replace('=', '')