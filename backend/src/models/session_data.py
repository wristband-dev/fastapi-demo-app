from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Any

from wristband.models import CallbackData, UserInfo

@dataclass
class SessionData:
    is_authenticated: bool
    access_token: str
    csrf_token: str
    expires_at: int
    tenant_domain_name: str
    tenant_custom_domain: str
    user_info: UserInfo
    refresh_token: str

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, str] = asdict(self)
        data['user_info'] = str(asdict(self.user_info))
        return data
    
    def to_session_init_data(self) -> dict[str, Any]:
        return {
            "tenantId": self.user_info.tnt_id,
            "userId": self.user_info.sub,
            "metadata": self.to_dict()
        }
    
    @staticmethod
    def from_callback_result_data(callback_data: CallbackData, csrf_token: str) -> 'SessionData':
        return SessionData(
            is_authenticated=True,
            access_token=callback_data.access_token,
            csrf_token=csrf_token,
            expires_at=int((datetime.now() + timedelta(seconds=callback_data.expires_in)).timestamp() * 1000),
            tenant_domain_name=callback_data.tenant_domain_name,
            tenant_custom_domain=callback_data.tenant_custom_domain or "",
            user_info=UserInfo.from_dict(callback_data.user_info),
            refresh_token=callback_data.refresh_token or ""
        )
    
    @staticmethod
    def from_dict(data: dict[str, Any]) -> 'SessionData':
        user_info_data = data.pop('user_info')
        
        # If user_info_data is a string, parse it into a dictionary
        if isinstance(user_info_data, str):
            import ast
            user_info_data = ast.literal_eval(user_info_data)
            
        user_info: UserInfo = UserInfo.from_dict(user_info_data)
        return SessionData(**data, user_info=user_info)
