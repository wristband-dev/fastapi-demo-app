from dataclasses import asdict, dataclass
from typing import Any, Optional


@dataclass
class SessionData:
    is_authenticated: bool = False
    access_token: str = ""
    expires_at: int = 0
    refresh_token: Optional[str] = None
    user_id: str = ""
    tenant_id: str = ""
    idp_name: str = ""
    tenant_domain_name: str = ""
    tenant_custom_domain: Optional[str] = None
    csrf_token: str = ""

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = asdict(self)
        return data

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "SessionData":
        return SessionData(**data)

    @staticmethod
    def empty() -> "SessionData":
        return SessionData()
