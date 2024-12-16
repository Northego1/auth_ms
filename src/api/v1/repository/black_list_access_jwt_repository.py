from datetime import datetime
from typing import Protocol, Self
import uuid
from sqlalchemy import select

from database.models import BlackListAccessJwtModel
from unit_of_work import UnitOfWorkProtocol, Uow
from dependency_injector import providers, containers


class AccessJwtBlackListRepositoryProtocol(Protocol):
    async def add_access_token(
            self: Self,
            jti: uuid.UUID,
            expire_at: datetime,
            access_token: str
    ):
        pass


    async def read_access_token(
            self: Self,
            jti: uuid.UUID
    ) -> BlackListAccessJwtModel | None:
        pass


class AccessJwtBlackListRepositoryImpl:
    def __init__(
            self: Self,
            uow: UnitOfWorkProtocol,
            ):
        self.uow: UnitOfWorkProtocol = uow

    async def add_access_token(
            self: Self,
            jti: uuid.UUID,
            expire_at: datetime,
            access_token: str
    ):
        async with self.uow as uow:
            new_record = BlackListAccessJwtModel(
                id=jti,
                access_token=access_token,
                expire_at=expire_at.replace(tzinfo=None)
            )
            uow.session.add(new_record)


    async def read_access_token(
            self: Self,
            jti: uuid.UUID
    ) -> BlackListAccessJwtModel | None:
        async with self.uow as uow:
            query = (
                select(BlackListAccessJwtModel)
                .where(BlackListAccessJwtModel.id == jti)
            )
            result = await uow.session.execute(query)
            record = result.scalar_one_or_none()
            return record


class Container(containers.DeclarativeContainer):
    repository = providers.Factory(
        AccessJwtBlackListRepositoryImpl,
        uow=Uow
    )

container = Container()

AccessTokenBlackListRepository = container.repository
