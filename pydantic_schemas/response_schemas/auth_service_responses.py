import uuid
from pydantic import BaseModel, EmailStr
from enum import Enum

from pydantic_schemas.jwt_schemas import AccessTokenSchema, RefreshTokenSchema
from pydantic_schemas.response_schemas.base_response_schema import DefaultMicroServiceResponseSchema


class MsLoginResponsePayload(BaseModel):
    access_token_info: AccessTokenSchema
    refresh_token_info: RefreshTokenSchema


class MsResponseLoginSchema(DefaultMicroServiceResponseSchema):
    """Response from the auth microserice auth, login endpoint."""
    payload: MsLoginResponsePayload | None = None


class MsResponseRegisterSchema(DefaultMicroServiceResponseSchema):
    username: str
    email: EmailStr


class MsResponseRefreshJwtSchema(DefaultMicroServiceResponseSchema):
    access_token_info: AccessTokenSchema


