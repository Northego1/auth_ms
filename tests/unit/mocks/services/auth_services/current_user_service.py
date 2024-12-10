from typing import cast
from unittest.mock import AsyncMock, Mock

from api.v1.services import auth_services
from exceptions import AuthError
from pydantic_schemas.from_orm.user_schema import UserSchema


MockCurrentUserService = cast(
    auth_services.CurrentUserServiceProtocol,
    Mock()
)
MockCurrentUserService.get_current_user = AsyncMock(
    return_value=UserSchema(
        id='e325db35-6ab9-4945-9a81-e2b5466938a6',
        username="test_user",
        hashed_password=b'test_pass',
        email='test@email.com',
        is_active=True
    )
)
