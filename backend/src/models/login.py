from dataclasses import dataclass, asdict
from typing import Optional

from flask import json

@dataclass
class LoginConfig:
    custom_state: Optional[dict[str, str]] = None
    default_tenant_custom_domain: Optional[str] = None
    default_tenant_domain: Optional[str] = None


@dataclass
class LoginState:
    state: str
    code_verifier: str
    redirect_uri: str
    return_url: Optional[str]
    custom_state: Optional[dict[str, str]]

    def to_dict(self) -> dict[str, str | dict[str, str]]:
        return asdict(self)
