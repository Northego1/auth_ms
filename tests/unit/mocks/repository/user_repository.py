from typing import Any, cast
from unittest.mock import AsyncMock, Mock
from exceptions import DatabaseError
from pydantic_schemas.from_orm.user_schema import UserSchema
from api.v1.repository.user_repository import (
    UserRepositoryProtocol
)
from tests.unit.config_data import mock_user


async def get_one_user_side_effect(
    searching_parameter: str,
    value: Any
) -> UserSchema | None:
    if searching_parameter == 'username':
        if value != mock_user.username:
            return None
        return mock_user
    elif searching_parameter == 'id':
        if value != mock_user.id:
            return None
        return mock_user
    

MockUserRepository = cast(
    UserRepositoryProtocol,
    Mock()
)
MockUserRepository.create_user = AsyncMock(
    return_value=mock_user
)
MockUserRepository.get_one_user = AsyncMock(
    side_effect=get_one_user_side_effect
)