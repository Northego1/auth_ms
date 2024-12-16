from typing import cast
from unittest.mock import AsyncMock, Mock
from api.v1.services import jwt_services
from exceptions import MicroServiceError
from pydantic_schemas.request_schemas.ms_request_schemas import MsRequestRegisterDto
from tests.unit.config_data import mock_access_token
from config import settings


def mock_decode_and_validate_jwt(token: str, token_type: str):
    if token != mock_access_token.token:
        raise MicroServiceError(status_code=403, detail='Токен некорректен или просрочен')
    if token_type != settings.jwt.access_type:
        raise MicroServiceError(status_code=403, detail="Неверный тип токена")

    return mock_access_token


MockAccessJwtService = cast(
    jwt_services.AccessTokenServiceProtocol,
    Mock()
)
MockAccessJwtService.create_token = Mock(
    return_value=mock_access_token
)
MockAccessJwtService.revoke_token = AsyncMock(
    return_value=None
)
MockAccessJwtService.check_access_token_blacklist = AsyncMock(
    return_value=None
)
MockAccessJwtService.decode_and_validate_jwt = Mock(
    side_effect=mock_decode_and_validate_jwt
)

