from typing import cast
from unittest.mock import AsyncMock, Mock
from pydantic_schemas.from_orm.user_schema import UserSchema
from api.v1.repository.user_repository import (
    UserRepositoryProtocol
)

return_value=UserSchema(
        id='e325db35-6ab9-4945-9a81-e2b5466938a6',
        username="test_user",
        hashed_password=b'test_pass',
        email='test@email.com',
        is_active=True
    )

MockUserRepository = cast(
    UserRepositoryProtocol,
    Mock()
)
MockUserRepository.create_user = AsyncMock(
    return_value=return_value
)
MockUserRepository.get_one_user = AsyncMock(
    return_value=return_value
)