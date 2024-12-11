from typing import Protocol, Self
import bcrypt

from api.v1.repository.user_repository import (
    UserRepository,
    UserRepositoryProtocol,
)

from api.v1.utils.password_utils import check_password
from database.models import UserModel
from exceptions import AuthError, MicroServiceError

from dependency_injector import containers, providers
from logger import message_logger as mes_log

from pydantic_schemas.from_orm.user_schema import UserSchema
from pydantic_schemas.request_schemas.ms_request_schemas import MsRequestLoginDto
from timer import timer

class UserAuthServiceProtocol(Protocol):
    def _verify_password(
            self: Self,
            hashed_password_from_request: bytes,
            hashed_password_from_db: bytes
    ):
        pass


    def _check_active_user(self: Self, user: UserSchema):
        pass
    

    async def authentificate_user(
            self: Self,
            user_login_schema: MsRequestLoginDto
    ) -> UserSchema:
        pass


class UserAuthServiceImpl:
    def __init__(
        self: Self,
        UserRepository: UserRepositoryProtocol
    ):
        self.UserRepository = UserRepository


    def _verify_password(
            self: Self,
            username: str,
            hashed_password_from_request: bytes,
            hashed_password_from_db: bytes
    ):
        if not check_password(
            hashed_password_from_request=hashed_password_from_request,
            hashed_password_from_db=hashed_password_from_db
        ):  
            mes_log.error(f"User {username} has incorrect password")
            raise AuthError(detail='Неправильный пароль')
            

    def _check_active_user(self: Self, user: UserSchema):
        if not user.is_active:
            mes_log.error(f"User {user.username} not active")
            raise AuthError(detail='Пользователь не активен')


    async def authentificate_user(
            self: Self,
            user_login_schema: MsRequestLoginDto
    ) -> UserSchema:
        
        mes_log.info(f'Trying to find user {user_login_schema.username!r}')
        user = await self.UserRepository.get_one_user(
            searching_parameter='username',
            value=user_login_schema.username
        )
        if not user:
            mes_log.info(f"User {user_login_schema.username!r} not found")
            raise AuthError(detail="Пользователь не найден")
        mes_log.info(f'User {user_login_schema.username!r} found, checking ...')
        self._check_active_user(user=user)
        self._verify_password(
            user_login_schema.username,
            hashed_password_from_request=user_login_schema.hashed_password,
            hashed_password_from_db=user.hashed_password
        )

        return user
    

class Container(containers.DeclarativeContainer):
    user_auth_service = providers.Factory(
        UserAuthServiceImpl,
        UserRepository=UserRepository
    )

container = Container()
UserAuthService = container.user_auth_service