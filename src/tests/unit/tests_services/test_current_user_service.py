from typing import Optional, Union
from dependency_injector import providers
from api.v1.services.auth_services.current_user_service import (
    container,
    CurrentUserServiceImpl
)
from exceptions import MicroServiceError
from pydantic_schemas.from_orm.user_schema import UserSchema
from pydantic_schemas.jwt_schemas import AccessTokenSchema, RefreshTokenSchema
from tests.unit.mocks import repository
import pytest
from tests.unit.config_data import mock_access_token


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "token_schema, expectation",
    [
        (
            mock_access_token,
            None
        ),
        (
            'non_correct',
            pytest.raises(MicroServiceError)
        )
    ]
)
async def test_current_user_service(
    token_schema: RefreshTokenSchema,
    expectation: Optional[pytest.raises]
):
    '''
    Юнит тест для сервиса нахождения текущего пользователя,
    перезаписываем зависимости на моки, 
    функция ожидает аксес токен схему, или рефреш токен схему
    функция возвращает "UserSchema", 
    в случае ошибки ожидаем "expectation"
    '''
    container.get_user_by_jwt.override(
        providers.Factory(
            CurrentUserServiceImpl,
            UserRepository=repository.MockUserRepository
        )
    )
    current_user_service = container.get_user_by_jwt()
    if expectation:
        with expectation:
            result = await current_user_service.get_current_user(
                token_schema=token_schema
            )
    else:
        result = await current_user_service.get_current_user(
                token_schema=token_schema
            )
        assert isinstance(result, UserSchema)