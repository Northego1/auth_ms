from contextlib import asynccontextmanager
from typing import Optional, Protocol, Self, Type
from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector import containers, providers

from exceptions import DatabaseError, MicroServiceError
from database.db_setup import get_db_session  


CONSTRAINT_ERROR_MESSAGES = {
    "users_email_key": "Текущий адрес почты уже существует",
    "unique_uuid": "Ошибка индетификатора",
    "users_username_key": "Имя пользователя уже занято"
}   


class UnitOfWorkProtocol(Protocol):
    session: AsyncSession

    async def __aenter__(self: Self) -> Self:
        pass


    async def __aexit__(
        self: Self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback
    ) -> None:
        pass


class UnitOfWorkImpl:
    def __init__(self: Self, session: AsyncSession):
        self.session = session

    async def __aenter__(self: Self):
        return self

    async def __aexit__(
        self: Self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback,
    ):
        try:
            if exc_type:
                await self.session.rollback()
                for constraint, user_message in CONSTRAINT_ERROR_MESSAGES.items():
                    if constraint in str(exc_value):
                        raise DatabaseError(
                            status_code=401,
                            detail=user_message
                        ) from exc_value
                raise DatabaseError(
                    detail=f'Ошибка базы данных: {exc_type}'
                ) from exc_value
            else:
                await self.session.commit()
        finally:
            await self.session.close()


@asynccontextmanager
async def provide_session():
    async for session in get_db_session():  
        yield session



class Container(containers.DeclarativeContainer):
    db_session = providers.Callable(
        lambda: provide_session().__aenter__()  
    )

    unit_of_work = providers.Factory(
        UnitOfWorkImpl,
        session=providers.Callable(lambda: provide_session().__aenter__())
    )


container = Container()
Uow: UnitOfWorkProtocol = container.unit_of_work()


container = Container()
Uow: UnitOfWorkProtocol = container.unit_of_work