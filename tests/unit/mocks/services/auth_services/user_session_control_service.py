from typing import cast
from unittest.mock import AsyncMock, Mock

from api.v1.services import auth_services
from exceptions import AuthError, DatabaseError, MicroServiceError
from pydantic_schemas.from_orm.user_schema import UserSchema
from pydantic_schemas.request_schemas.ms_request_schemas import MsRequestRegisterDto


MockUserSessionService = cast(
    auth_services.UserSessionServiceProtocol,
    Mock()
)


MockUserSessionService.register_user_session = AsyncMock(
    return_value=None
)
MockUserSessionService.check_and_invalidate_session = AsyncMock(
    return_value=None
)
MockUserSessionService._create_or_replace_session = AsyncMock(
    return_value=None
)
MockUserSessionService._create_session = AsyncMock(
    return_value=None
)
MockUserSessionService._update_session_if_exist = AsyncMock(
    return_value=None
)