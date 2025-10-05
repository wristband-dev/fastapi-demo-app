from pydantic import BaseModel, ConfigDict


class HelloWorldResponse(BaseModel):
    model_config = ConfigDict(serialize_by_alias=True)

    message: str


class NicknameResponse(BaseModel):
    model_config = ConfigDict(serialize_by_alias=True)

    nickname: str
