from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class HelloWorldResponse(BaseModel):
    model_config = ConfigDict(serialize_by_alias=True)

    message: str


class NicknameResponse(BaseModel):
    model_config = ConfigDict(serialize_by_alias=True)

    nickname: str


class SessionData(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    is_authenticated: bool = Field(
        default=False, validation_alias="isAuthenticated", serialization_alias="isAuthenticated"
    )
    access_token: str = Field(default="", validation_alias="accessToken", serialization_alias="accessToken")
    expires_at: int = Field(default=0, validation_alias="expiresAt", serialization_alias="expiresAt")
    refresh_token: Optional[str] = Field(
        default=None, validation_alias="refreshToken", serialization_alias="refreshToken"
    )
    user_id: str = Field(default="", validation_alias="userId", serialization_alias="userId")
    tenant_id: str = Field(default="", validation_alias="tenantId", serialization_alias="tenantId")
    idp_name: str = Field(default="", validation_alias="idpName", serialization_alias="idpName")
    tenant_domain_name: str = Field(
        default="", validation_alias="tenantDomainName", serialization_alias="tenantDomainName"
    )
    tenant_custom_domain: Optional[str] = Field(
        default=None, validation_alias="tenantCustomDomain", serialization_alias="tenantCustomDomain"
    )
    csrf_token: str = Field(default="", validation_alias="csrfToken", serialization_alias="csrfToken")

    @staticmethod
    def empty() -> "SessionData":
        return SessionData()


class SessionResponse(BaseModel):
    model_config = ConfigDict(serialize_by_alias=True)

    tenant_id: str = Field(serialization_alias="tenantId")
    user_id: str = Field(serialization_alias="userId")
    metadata: SessionData


class TokenResponse(BaseModel):
    model_config = ConfigDict(serialize_by_alias=True)

    access_token: str = Field(serialization_alias="accessToken")
    expires_at: int = Field(serialization_alias="expiresAt")
