from typing import Any, Protocol, Self
from uuid import uuid4
from pydantic import EmailStr
from sqlalchemy import select

from database.models import UserModel


from pydantic_schemas.from_orm.user_schema import UserSchema
from timer import timer
from unit_of_work import UnitOfWorkProtocol, Uow
from dependency_injector import containers, providers



class UserRepositoryProtocol(Protocol):
    async def get_one_user(
            self: Self,
            searching_parameter: str,
            value: Any
    ) -> UserSchema | None:
        pass


    async def create_user(
            self: Self,
            username: str,
            hashed_password: bytes,
            email: EmailStr
    ) -> UserSchema:
        pass

    async def update_user(self: Self):
        pass


    async def delete_user(self: Self):
        pass


class UserRepositoryImpl:
    def __init__(self, uow: UnitOfWorkProtocol):
        self.uow = uow


    async def get_one_user(
            self: Self,
            searching_parameter: str,
            value: Any
    ) -> UserSchema | None:
        async with self.uow as uow:
            query = (
                select(UserModel)
                .where(getattr(UserModel, searching_parameter) == value)
            )
            result = await uow.session.execute(query)
            user = result.scalar_one_or_none()
            return UserSchema.model_validate(user) if user else None


    async def create_user(
            self: Self,
            username: str,
            hashed_password: bytes,
            email: EmailStr
    ) -> UserSchema | None:
        async with self.uow as uow:
            new_user = UserModel(
                id=uuid4(),
                username=username,
                hashed_password=hashed_password,
                email=email,
                is_active=True,
            )
            uow.session.add(new_user)
            await uow.session.flush()
            return UserSchema.model_validate(new_user) if new_user else None


    async def update_user(
            self: Self, 
            user_id: int
    ):
        pass


    async def delete_user(
            self: Self
    ):
        pass



class Container(containers.DeclarativeContainer):
    uow = providers.Factory(Uow)


    user_repository = providers.Factory(
        UserRepositoryImpl,
        uow=uow,
    )


container = Container()
UserRepository: UserRepositoryProtocol = container.user_repository
