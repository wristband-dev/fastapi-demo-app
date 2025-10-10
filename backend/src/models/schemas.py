from pydantic import BaseModel, ConfigDict
from wristband.fastapi_auth import Session
from typing import Optional, Protocol


# WRISTBAND_TOUCHPOINT: Extend Session Protocol
class MySession(Session, Protocol):
    custom_field: Optional[str]


class HelloWorldResponse(BaseModel):
    model_config = ConfigDict(serialize_by_alias=True)

    message: str


class NicknameResponse(BaseModel):
    model_config = ConfigDict(serialize_by_alias=True)

    nickname: str
