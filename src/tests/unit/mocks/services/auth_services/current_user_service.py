from typing import cast
from unittest.mock import AsyncMock, Mock

from api.v1.services import auth_services
from pydantic_schemas.from_orm.user_schema import UserSchema
from tests.unit.config_data import mock_user


MockCurrentUserService = cast(
    auth_services.CurrentUserServiceProtocol,
    Mock()
)
MockCurrentUserService.get_current_user = AsyncMock(
    return_value=mock_user
)
