from typing import cast
from unittest.mock import AsyncMock, Mock

from api.v1.services import auth_services


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