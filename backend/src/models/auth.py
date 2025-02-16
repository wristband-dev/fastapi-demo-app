from dataclasses import dataclass, asdict, field
from typing import Optional, List

@dataclass
class AuthConfig:
    client_id: str
    client_secret: str
    login_state_secret: str
    login_url: str
    redirect_uri: str
    wristband_application_domain: str

    custom_application_login_page_url: Optional[str] = None
    dangerously_disable_secure_cookies: bool = False
    root_domain: Optional[str] = None
    scopes: List[str] = field(default_factory=lambda: ['openid', 'offline_access', 'email'])
    use_custom_domains: bool = False
    use_tenant_subdomains: bool = False