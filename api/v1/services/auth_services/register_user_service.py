from typing import Protocol, Self


from api.v1.repository.user_repository import UserRepositoryProtocol, UserRepository
from api.v1.utils.password_utils import hash_password
from exceptions import DatabaseError, MicroServiceError

from dependency_injector import providers, containers


from pydantic_schemas.from_orm.user_schema import UserSchema
from pydantic_schemas.request_schemas.ms_request_schemas import MsRequestRegisterDto


class RegiserUserServiceProtocol(Protocol):
    async def register_user(
            self: Self,
            user_regiser_schema: MsRequestRegisterDto
    ) -> UserSchema:
        pass


class RegisterUserServiceImpl:
    def __init__(
            self,
            UserRepository: UserRepositoryProtocol,       
    ):
        self.UserRepository = UserRepository
    
    
    async def register_user(
            self: Self,
            user_register_schema: MsRequestRegisterDto
    ) -> UserSchema:
        try:
            user: UserSchema = await self.UserRepository.create_user(
                username=user_register_schema.username,
                hashed_password=user_register_schema.hashed_password,
                email=user_register_schema.email
            )
            return user
        except DatabaseError as e:
            raise MicroServiceError(
                status_code=e.status_code,
                detail=e.detail
            ) from e


class Container(containers.DeclarativeContainer):
    register_service = providers.Factory(
        RegisterUserServiceImpl,
        UserRepository=UserRepository
    )

container = Container()
RegisterUserService = container.register_service
