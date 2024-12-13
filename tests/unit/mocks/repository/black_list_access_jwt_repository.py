from datetime import datetime, timedelta, timezone
from typing import cast
from unittest.mock import AsyncMock, Mock
from uuid import uuid4
from database.models import BlackListAccessJwtModel
from pydantic_schemas.from_orm.user_schema import UserSchema
from api.v1.repository.black_list_access_jwt_repository import (
    AccessJwtBlackListRepositoryProtocol
)
from config import settings


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
