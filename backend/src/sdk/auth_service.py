import base64
import os
import secrets
import time
import json
from typing import Any, Optional, Union
from urllib.parse import urlencode
import hashlib
from flask import Request, Response, make_response
from cryptography.fernet import Fernet

from src.sdk.wristband_service import WristbandService
from src.sdk.enums import CallbackResultType
from src.sdk.models import CallbackData, CallbackResult, LoginConfig, LoginState, AuthConfig


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

        self.wristband_service = WristbandService(
            wristband_application_domain=self.wristband_application_domain,
            client_id=self.client_id,
            client_secret=self.client_secret
        )


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

    def callback(self, req: Request) -> CallbackResult:
        """
        """
        # 1) Extract Query Params from wristband callback
        code = req.args.get('code')
        param_state = req.args.get('state')
        error = req.args.get('error')
        error_description = req.args.get('error_description')
        tenant_custom_domain_param = req.args.get('tenant_custom_domain')

        # 2) Validate basic query params
        if not param_state or not isinstance(param_state, str):
            raise TypeError('Invalid or missing query parameter [state].')

        if code and not isinstance(code, str):
            raise TypeError('Invalid query parameter [code].')

        if error and not isinstance(error, str):
            raise TypeError('Invalid query parameter [error].')

        if error_description and not isinstance(error_description, str):
            raise TypeError('Invalid query parameter [error_description].')

        if tenant_custom_domain_param and not isinstance(tenant_custom_domain_param, str):
            raise TypeError('Invalid query parameter [tenant_custom_domain].')

        # 3) Resolve tenant domain name
        resolved_tenant_domain_name: str = self._resolve_tenant_domain_name(req, self.root_domain)
        if not resolved_tenant_domain_name:
            # useTenantSubdomains is a design choice; adapt as needed
            if self.use_tenant_subdomains:
                raise ValueError(
                    'missing_tenant_subdomain: Callback request URL is missing a tenant subdomain'
                )
            else:
                raise ValueError(
                    'missing_tenant_domain: Callback request is missing the [tenant_domain] param'
                )

        # 4) Build the tenant login URL in case we need to redirect
        #    (mimics the logic from your TypeScript code)
        if self.use_tenant_subdomains:
            tenant_login_url = self.login_url.replace("{tenant_domain}", resolved_tenant_domain_name)
        else:
            # fallback, append ?tenant_domain=...
            tenant_login_url = f"{self.login_url}?tenant_domain={resolved_tenant_domain_name}"

        # If the tenant_custom_domain is set, add that param
        if tenant_custom_domain_param:
            # If we already used ? above, use & now, etc.
            connector = '&' if '?' in tenant_login_url else '?'
            tenant_login_url = f"{tenant_login_url}{connector}tenant_custom_domain={tenant_custom_domain_param}"

        # Create a login redirect response for bad cases
        login_redirect_res = make_response()
        login_redirect_res.headers['Cache-Control'] = 'no-store'
        login_redirect_res.headers['Pragma'] = 'no-cache'
        login_redirect_res.status_code = 302
        login_redirect_res.headers['Location'] = tenant_login_url

        # 5) Retrieve and decrypt the login state cookie
        login_state_cookie_name, login_state_cookie_val = self._get_login_state_cookie(req)

        if not login_state_cookie_val:
            # No valid cookie => We cannot verify the request => redirect to login
            return CallbackResult(
                result=CallbackResultType.REDIRECT_REQUIRED,
                callback_data=None,
                redirect_response=login_redirect_res
            )

        try:
            login_state: LoginState = self._decrypt_login_state(login_state_cookie_val, self.login_state_secret)
        except Exception as e:
            # If decryption fails, redirect to login
            return CallbackResult(
                result=CallbackResultType.REDIRECT_REQUIRED,
                callback_data=None,
                redirect_response=login_redirect_res
            )
        
        # 6) Validate the state from the cookie matches the incoming state param
        if param_state != login_state.state:
            # Mismatch => redirect
            return CallbackResult(
                result=CallbackResultType.REDIRECT_REQUIRED,
                callback_data=None,
                redirect_response=login_redirect_res
            )

        # 7) Check for any OAuth errors
        if error:
            # If we specifically got a 'login_required' error, go back to the login
            if error.lower() == 'login_required':
                return CallbackResult(
                    result=CallbackResultType.REDIRECT_REQUIRED,
                    callback_data=None,
                    redirect_response=login_redirect_res
                )
            # Otherwise raise an exception
            raise ValueError(f"OAuth error: {error}. Description: {error_description}")

        # 8) If no code, this is an error
        if not code:
            raise TypeError('Missing required query parameter [code].')

        # 9) Exchange the authorization code for tokens
        #    Here you would call your Wristband token endpoint. Example:


        token_response = self.wristband_service.get_tokens(
            code=code,
            redirect_uri=login_state.redirect_uri,
            code_verifier=login_state.code_verifier
        )

        # 10) Fetch userinfo (again, depends on your own implementation)
        userinfo: dict[str, Any] = self.wristband_service.get_userinfo(token_response.access_token)

        callback_data: CallbackData = CallbackData(
            access_token=token_response.access_token,
            id_token=token_response.id_token,
            expires_in=token_response.expires_in,
            tenant_domain_name=resolved_tenant_domain_name,
            user_info=userinfo,
            custom_state=login_state.custom_state,
            refresh_token=token_response.refresh_token,
            return_url=login_state.return_url,
            tenant_custom_domain=tenant_custom_domain_param
        )

        return CallbackResult(
            result=CallbackResultType.COMPLETED,
            callback_data=callback_data,
            redirect_response=None
        )

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
        
    def _get_login_state_cookie(self, req: Request) -> tuple:
        cookies = req.cookies
        state = req.args.get('state')
        param_state = state if state else ''

        matching_login_cookie_names = [
            cookie_name for cookie_name in cookies
            if cookie_name.startswith(f"{self._cookie_prefix}{param_state}{self._login_state_cookie_separator}")
        ]

        if matching_login_cookie_names:
            cookie_name = matching_login_cookie_names[0]
            return cookie_name, cookies[cookie_name]

        return None, None
    
    def _decrypt_login_state(self, login_state_cookie: str, login_state_secret: str) -> LoginState:
        key = base64.urlsafe_b64encode(login_state_secret.encode().ljust(32)[:32])
        f = Fernet(key)
        decrypted = f.decrypt(login_state_cookie.encode('utf-8'))
        login_state_dict = json.loads(decrypted.decode('utf-8'))
        return LoginState(**login_state_dict)