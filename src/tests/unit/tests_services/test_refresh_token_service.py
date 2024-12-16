from typing import Optional
import pytest

from exceptions import MicroServiceError
from pydantic_schemas.from_orm.user_schema import UserSchema
from api.v1.services.jwt_services.refresh_jwt_service import (
    container,
    RefreshJwtServiceImpl
)
from dependency_injector import providers
from pydantic_schemas.jwt_schemas import RefreshTokenSchema
from unit.mocks import repository
from unit.config_data import mock_user, mock_access_token



@pytest.mark.parametrize(
    "mock_user, expectation",
    [
        (
            mock_user,
            None
        ),
    ]
)
def test_create_token(
    mock_user: UserSchema,
    expectation: Optional[pytest.raises]
):
    '''
    Юнит тест для сервиса создания рефреш токена, перезаписываем зависимости на моки, 
    функция ожидает аксес токен схему, функция возвращает рефреш токен схему, 
    в случае ошибки ожидаем "expectation"
    '''
    container.refresh_jwt_service.override(
        providers.Factory(
            RefreshJwtServiceImpl,
            UserSessionRepository=repository.MockUserSessionRepository
        )
    )
    refresh_token_service = container.refresh_jwt_service()
    if expectation:
        with expectation:
            result = refresh_token_service.create_token(
                user=mock_user
            )
    else:
        result = refresh_token_service.create_token(
            user=mock_user
        )
        assert isinstance(result, RefreshTokenSchema)

