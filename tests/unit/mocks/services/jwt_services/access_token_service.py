from datetime import datetime, timedelta, timezone
from typing import cast
from unittest.mock import AsyncMock, Mock
import uuid

from api.v1.services import jwt_services
from exceptions import AuthError, DatabaseError, MicroServiceError
from pydantic_schemas.from_orm.user_schema import UserSchema
from pydantic_schemas.jwt_schemas import AccessTokenPayloadSchema, AccessTokenSchema
from pydantic_schemas.request_schemas.ms_request_schemas import MsRequestRegisterDto
from config import settings


def mock_create_token(user: UserSchema):
    try:
        payload = AccessTokenPayloadSchema(
            type=settings.jwt.access_type,
            sub=user.username,
            user_id=user.id,
            jti=uuid.uuid4(),
            email=user.email,
            exp=datetime.now(timezone.utc) + timedelta(
                minutes=settings.jwt.access_expire
            )
        )
        access_token_schema = AccessTokenSchema(
            token='access_token',
            token_type=settings.jwt.access_type,
            payload=payload
        )
        return access_token_schema
    except Exception as e:
        raise MicroServiceError(detail='Неизвестая ошибка создания токена доступа')


MockAccessJwtService = cast(
    jwt_services.AccessTokenServiceProtocol,
    Mock()
)
MockAccessJwtService.create_token = Mock(
    side_effect=mock_create_token
)
MockAccessJwtService.revoke_token = AsyncMock(
    return_value=None
)
MockAccessJwtService.check_access_token_blacklist = AsyncMock(
    return_value=None
)
