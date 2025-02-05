import base64
import hashlib
import os
import secrets
from typing import Optional
from urllib.parse import urlencode
from flask import Request, Response, redirect
from cryptography.fernet import Fernet
import json

from src.models.login import LoginConfig, LoginState


class AuthService:
    def __init__(self, req: Request, res: Response, config: Optional[LoginConfig] = None):
        self.req = req
        self.res = res
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


    def login(self) -> str:
        # Redirect if no domain is determined
        if not any([self.tenant_custom_domain, self.tenant_domain_name, self.default_tenant_custom_domain, self.default_tenant_domain_name]):
            return f'https://{os.environ.get("APPLICATION_VANITY_DOMAIN")}/login'

        # Create and manage login state
        self.login_state: LoginState = self.create_login_state(
            redirect_uri='https://localhost:8080/api/auth/callback',
            config=self.config
        )
        self._manage_login_state_cookies()
        return self.get_oauth_authorize_url()

    def _disable_caching(self):
        """Disable caching by setting appropriate headers."""
        self.res.headers['Cache-Control'] = 'no-store'
        self.res.headers['Pragma'] = 'no-cache'

    def _resolve_tenant_domain(self, resolve_method) -> str:
        """Resolve tenant domain using the provided method."""
        return resolve_method()

    def _get_default_domain(self, domain_attr: str) -> str:
        """Get default domain from config."""
        return getattr(self.config, domain_attr, '') if self.config else ''

    def _manage_login_state_cookies(self):
        """Clear old login state cookies and set a new one."""
        self.clear_oldest_login_state_cookie(self.req, self.res)
        encrypted_login_state = self.encrypt_login_state(self.login_state, '7ffdbecc-ab7d-4134-9307-2dfcc52f7475')
        self.create_login_state_cookie(self.res, self.login_state.state, encrypted_login_state, True)

    def resolve_tenant_from_domain(self) -> str:
        """Resolve tenant domain name from request."""
        tenant = self._parse_tenant_subdomain()
        if tenant:
            return tenant

        tenant_domain = self.req.args.get('tenant_domain')
        if tenant_domain and isinstance(tenant_domain, list):
            raise TypeError('More than one [tenant_domain] query parameter was encountered')

        return tenant_domain or ''

    def resolve_tenant_from_custom_domain(self) -> str:
        """Resolve tenant from custom domain mapping."""
        host = self._get_host_without_port()
        return self.config.custom_state.get(host, '') if self.config and self.config.custom_state else ''

    def _get_host_without_port(self) -> str:
        """Get host from request without port."""
        host = self.req.host
        return host.split(':')[0] if ':' in host else host

    def create_login_state(self, redirect_uri: str, config: Optional[LoginConfig] = None) -> LoginState:
        """Create login state with PKCE code verifier and optional custom state."""
        return_url = self.req.args.get('return_url')
        if return_url and isinstance(return_url, list):
            raise TypeError('More than one [return_url] query parameter was encountered')

        return LoginState(
            state=self._generate_random_string(32),
            code_verifier=self._generate_random_string(32),
            redirect_uri=redirect_uri,
            return_url=return_url if return_url else None,
            custom_state=config.custom_state if config and config.custom_state else None
        )

    def clear_oldest_login_state_cookie(self, req: Request, res: Response):
        """Clear the oldest login state cookie if there are 3 or more login state cookies present."""
        if not req.cookies:
            raise ValueError('Please verify that your server is configured to handle cookies correctly.')

        login_cookie_names = [name for name in req.cookies.keys() if name.startswith(self.cookie_prefix)]
        if len(login_cookie_names) >= 3:
            timestamps = [name.split(self.login_state_cookie_separator)[2] for name in login_cookie_names]
            newest_timestamps = sorted(timestamps, reverse=True)[:2]
            for cookie_name in login_cookie_names:
                timestamp = cookie_name.split(self.login_state_cookie_separator)[2]
                if timestamp not in newest_timestamps:
                    res.delete_cookie(cookie_name)

    def encrypt_login_state(self, login_state: LoginState, login_state_secret: str) -> bytes:
        """Encrypt login state using Fernet symmetric encryption."""
        key = Fernet.generate_key()
        f = Fernet(login_state_secret.encode())
        encrypted_login_state = f.encrypt(json.dumps(login_state.to_dict()).encode('utf-8'))

        if len(encrypted_login_state) > 4096:
            raise TypeError('Login state cookie exceeds 4kB in size. Ensure your [customState] and [returnUrl] values are a reasonable size.')

        return encrypted_login_state

    def create_login_state_cookie(self, res: Response, state: str, encrypted_login_state: bytes, dangerously_disable_secure_cookies: bool = False):
        """Create a login state cookie."""
        import time
        encrypted_str = encrypted_login_state.decode('utf-8')
        res.set_cookie(
            self.cookie_prefix + state + self.login_state_cookie_separator + str(time.time()),
            encrypted_str,
            max_age=3600,
            secure=not dangerously_disable_secure_cookies
        )

    def _parse_tenant_subdomain(self) -> str:
        """Parse tenant name from subdomain."""
        if not self.config or not self.config.default_tenant_domain:
            return ''

        host = self._get_host_without_port()
        if host.endswith(self.config.default_tenant_domain):
            return host[:-len(self.config.default_tenant_domain)-1]

        return ''

    def _generate_random_string(self, length: int) -> str:
        """Generate a random string of specified length using URL-safe characters."""
        random_bytes = secrets.token_bytes(length)
        random_string = base64.urlsafe_b64encode(random_bytes).decode('utf-8')
        return random_string.rstrip('=')[:length]
    
    def get_oauth_authorize_url(self) -> str:
       
        login_hint = self.req.args.get('login_hint')
        if login_hint and isinstance(login_hint, list):
            raise TypeError('More than one [login_hint] query parameter was encountered')

        # Build query parameters
        query_params = {
            'client_id': "6y53fp4tjreqje74seffvq4idy",
            'redirect_uri': 'https://localhost:8080/api/auth/callback', 
            'response_type': 'code',
            'state': self.login_state.state,
            'scope': ' '.join(['openid', 'offline_access', 'profile', 'email', 'roles']),
            'code_challenge': self._base64_url_encode(hashlib.sha256(self.login_state.code_verifier.encode()).digest()),
            'code_challenge_method': 'S256',
            'nonce': self._generate_random_string(32)
        }
        
        if login_hint:
            query_params['login_hint'] = login_hint

        separator = '.' if self.config and self.config.tenant_custom_domain else '-'
        
        # Domain priority resolution
        if self.tenant_custom_domain != '':
            return f"https://{self.tenant_custom_domain}/api/v1/oauth2/authorize?{urlencode(query_params)}"
            
        if self.tenant_domain_name != '':
            return f"https://{self.tenant_domain_name}{separator}{os.environ.get('APPLICATION_VANITY_DOMAIN')}/api/v1/oauth2/authorize?{urlencode(query_params)}"
            
        if self.default_tenant_custom_domain:
            return f"https://{self.default_tenant_custom_domain}/api/v1/oauth2/authorize?{urlencode(query_params)}"
            
        return f"https://{self.default_tenant_domain_name}{separator}{os.environ.get('APPLICATION_VANITY_DOMAIN')}/api/v1/oauth2/authorize?{urlencode(query_params)}"
    
    def _base64_url_encode(self, data: bytes) -> str:
        """
        Base64 URL encode the given bytes data.
        
        Args:
            data: Bytes to encode
            
        Returns:
            str: Base64 URL encoded string with +/= chars replaced
        """
        # Convert bytes to base64 string and replace chars
        b64 = base64.b64encode(data).decode()
        return b64.replace('+', '-').replace('/', '_').replace('=', '')