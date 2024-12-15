from typing import cast
from unittest.mock import AsyncMock, Mock
from api.v1.services import jwt_services
from exceptions import MicroServiceError
from pydantic_schemas.request_schemas.ms_request_schemas import MsRequestRegisterDto
from config import settings
from tests.unit.config_data import mock_refresh_token


def mock_decode_and_validate_jwt(token: str, token_type: str):
    if token != mock_refresh_token.token:
        raise MicroServiceError(status_code=403, detail='Токен некорректен или просрочен')
    if token_type != settings.jwt.refresh_type:
        raise MicroServiceError(status_code=403, detail="Неверный тип токена")
    return mock_refresh_token


MockRefreshJwtService = cast(
    jwt_services.RefreshJwtServiceProtocol,
    Mock()
)
MockRefreshJwtService.create_token = Mock(
    return_value=mock_refresh_token
)
MockRefreshJwtService.revoke_token = AsyncMock(
    return_value=None
)
MockRefreshJwtService.decode_and_validate_jwt = Mock(
    side_effect=mock_decode_and_validate_jwt
)

