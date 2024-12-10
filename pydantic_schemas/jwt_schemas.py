from datetime import datetime
from enum import Enum
from typing import Self
import uuid
from pydantic import BaseModel, EmailStr
from config import settings


class TokenTransportType(Enum):
    COOKIE: str = 'cookie'
    BEARER: str = 'bearer'


class RefreshTokenPayloadSchema(BaseModel):
    type: str
    sub: str
    user_id: uuid.UUID
    jti: uuid.UUID
    exp: datetime

    def model_dump(self: Self, **kwargs) -> dict:
        data = super().model_dump(**kwargs)
        data['user_id'] = str(data['user_id'])
        data['jti'] = str(data['jti'])
        return data


class AccessTokenPayloadSchema(RefreshTokenPayloadSchema):
    email: EmailStr


class AccessTokenSchema(BaseModel):
    token: str
    token_type: str = settings.jwt.access_type
    transport_type: TokenTransportType = TokenTransportType.BEARER
    payload: AccessTokenPayloadSchema


class RefreshTokenSchema(BaseModel):
    token: str
    token_type: str = settings.jwt.refresh_type
    transport_type: TokenTransportType = TokenTransportType.COOKIE
    payload: RefreshTokenPayloadSchema