from datetime import datetime, timedelta, timezone
from typing import cast
from unittest.mock import AsyncMock, Mock
import uuid
from database.models import UserSessionModel
from api.v1.repository.user_session_repository import (
    UserSessionRepositoryProtocol
)
from config import settings


MockUserSessionRepository = cast(
    UserSessionRepositoryProtocol,
    Mock()
)
MockUserSessionRepository.create_user_session = AsyncMock(
    return_value = UserSessionModel(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        fingerprint_hash=b'mozilla',
        refresh_token='refresh_token',
        expire_at=datetime.now(timezone.utc) + timedelta(settings.jwt.refresh_expire),
        session_num=5
    )
)
MockUserSessionRepository.update_user_session = AsyncMock(
    return_value=None
)
MockUserSessionRepository.is_session_exist = AsyncMock(
    return_value=False
)
MockUserSessionRepository.count_user_sessions = AsyncMock(
    return_value=5
)
MockUserSessionRepository.delete_user_session = AsyncMock(
    return_value=True
)
MockUserSessionRepository.delete_session_if_fingerprint_invalid = AsyncMock(
    return_value=True
)
