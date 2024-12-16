from datetime import datetime, timedelta, timezone
from typing import cast
from unittest.mock import AsyncMock, Mock
from uuid import uuid4
import uuid
from database.models import BlackListAccessJwtModel
from exceptions import DatabaseError
from pydantic_schemas.from_orm.user_schema import UserSchema
from api.v1.repository.black_list_access_jwt_repository import (
    AccessJwtBlackListRepositoryProtocol
)
from config import settings
from unit.config_data import mock_access_token


async def mock_read_access_token(
        jti: uuid.UUID
) -> BlackListAccessJwtModel | None:
    if jti != mock_access_token.payload.jti:
        raise DatabaseError()
    return BlackListAccessJwtModel(
            id=mock_access_token.payload.jti,
            access_token=mock_access_token.token,
            expire_at=mock_access_token.payload.exp
        )
        

MockAccessTokenBlackListRepository = cast(
    AccessJwtBlackListRepositoryProtocol,
    Mock()
)
MockAccessTokenBlackListRepository.add_access_token = AsyncMock(
    return_value=None
)
MockAccessTokenBlackListRepository.read_access_token = AsyncMock(
    return_value=BlackListAccessJwtModel(
        id=uuid4(),
        access_token='access_token',
        expire_at=datetime.now(timezone.utc) + timedelta(settings.jwt.access_expire)
    )
)
