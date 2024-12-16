from typing import Literal, Protocol, Self, Union

from api.v1.repository.user_repository import UserRepositoryProtocol, UserRepository
from database.models import UserModel
from exceptions import DatabaseError, MicroServiceError

from pydantic_schemas.from_orm.user_schema import UserSchema
from pydantic_schemas.jwt_schemas import AccessTokenSchema, RefreshTokenSchema
from dependency_injector import providers, containers


class CurrentUserServiceProtocol(Protocol):
    async def get_current_user(
        self: Self,
        token_schema: Union[AccessTokenSchema, RefreshTokenSchema],
    ) -> UserSchema:
        pass


class CurrentUserServiceImpl:
    def __init__(
        self: Self,
        UserRepository: UserRepositoryProtocol
    ):
        self.UserRepository: UserRepositoryProtocol = UserRepository

    async def get_current_user(
        self: Self,
        token_schema: Union[AccessTokenSchema, RefreshTokenSchema],
    ) -> UserSchema:
        try:
            user: UserModel = await self.UserRepository.get_one_user(
                searching_parameter='id',
                value=token_schema.payload.user_id
            )
            return user
        except DatabaseError as e:
            raise MicroServiceError(
                status_code=e.status_code,
                detail=e.detail
            )
        except Exception as e:
            raise MicroServiceError()


class Container(containers.DeclarativeContainer):
    get_user_by_jwt = providers.Factory(
        CurrentUserServiceImpl,
        UserRepository=UserRepository
    )


container = Container()
CurrentUserService = container.get_user_by_jwt
