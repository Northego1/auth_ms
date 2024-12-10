from datetime import datetime, timedelta, timezone
from typing import cast
from unittest.mock import AsyncMock, Mock
import uuid

from api.v1.services import jwt_services
from exceptions import AuthError, DatabaseError, MicroServiceError
from pydantic_schemas.from_orm.user_schema import UserSchema
from pydantic_schemas.jwt_schemas import AccessTokenPayloadSchema, AccessTokenSchema, RefreshTokenPayloadSchema, RefreshTokenSchema
from pydantic_schemas.request_schemas.ms_request_schemas import MsRequestRegisterDto
from config import settings


async def mock_create_token(user: UserSchema):
    try:
        payload = RefreshTokenPayloadSchema(
                type=settings.jwt.refresh_type,
                sub=user.username,
                user_id=user.id,
                jti=uuid.uuid4(),
                exp=datetime.now(timezone.utc) + timedelta(
                    minutes=settings.jwt.refresh_expire
                )
            )
        refresh_token_schema = RefreshTokenSchema(
            token='refresh_token',
            token_type=settings.jwt.refresh_type,
            payload=payload
        )
        return refresh_token_schema
    except Exception as e:
        raise MicroServiceError(detail='Неизвестая ошибка создания рефреш токена')



MockRefreshJwtService = cast(
    jwt_services.RefreshJwtServiceProtocol,
    Mock()
)
MockRefreshJwtService.create_token = AsyncMock(
    side_effect=mock_create_token
)
MockRefreshJwtService.revoke_token = AsyncMock(
    return_value=None
)

