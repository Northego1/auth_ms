from datetime import datetime, timezone
from typing import Optional, Self, Protocol
import uuid
from sqlalchemy import delete, select, update, func
from typing import Any

from config import settings
from database.models import UserSessionModel
from exceptions import MicroServiceError
from unit_of_work import UnitOfWorkProtocol, Uow
from dependency_injector import containers, providers


class UserSessionRepositoryProtocol(Protocol):
    async def create_user_session(
            self: Self,
            refresh_token: str,
            fingerprint_hash: bytes,
            expire_at: datetime,
            user_id: uuid.UUID,
    ) -> UserSessionModel:
        pass


    async def update_user_session(
            self: Self,
            fingerprint_hash: bytes,
            user_id: uuid.UUID,
            refresh_token: str,
            expire_at: datetime
    ) -> None:
        pass
    

    async def is_session_exist(
            self: Self,
            fingerprint_hash: bytes,
            user_id: uuid.UUID
    ) -> bool:
        pass


    async def count_user_sessions(self: Self, user_id: uuid.UUID) -> int | None:
        pass
    

    async def delete_user_session(
        self: Self,
        user_id: uuid.UUID,
        value: Any = None,
        delete_by: Optional[str] = None,
    ):
        pass


    async def delete_session_if_fingerprint_invalid(
            self: Self,
            user_id: uuid.UUID,
            refresh_token: str,
            fingerprint_hash: bytes
    ) -> bool:
        pass


class UserSessionRepositoryImpl:
    def __init__(self: Self, uow: UnitOfWorkProtocol,
    ):
        self.uow: UnitOfWorkProtocol = uow


    async def create_user_session(
            self: Self,
            refresh_token: str,
            fingerprint_hash: bytes,
            expire_at: datetime,
            user_id: uuid.UUID,
    ) -> UserSessionModel:
        async with self.uow as uow:
            query= (
                select(UserSessionModel.session_num)
                .where(UserSessionModel.user_id == user_id)
                .order_by(UserSessionModel.session_num)
            )
            sessions = await uow.session.execute(query)
            session_nums = [row[0] for row in sessions]

            for num in range(1, settings.jwt.max_user_sessions + 1):
                if num not in session_nums:
                    break
            new_record = UserSessionModel(
                id=uuid.uuid4(),
                refresh_token=refresh_token,
                fingerprint_hash=fingerprint_hash,
                expire_at=expire_at,
                user_id=user_id,
                session_num=num
            )
            uow.session.add(new_record)
            await uow.session.flush()
            return new_record


    async def update_user_session(
            self: Self,
            fingerprint_hash: bytes,
            user_id: uuid.UUID,
            refresh_token: str,
            expire_at: datetime
    ) -> None:
        async with self.uow as uow:
            stmt = (
                update(UserSessionModel)
                .where(
                    UserSessionModel.user_id == user_id,
                    UserSessionModel.fingerprint_hash == fingerprint_hash,
                )
                .values(
                    refresh_token=refresh_token,
                    expire_at=expire_at
                )
            )
            await uow.session.execute(stmt)


    async def is_session_exist(
            self: Self,
            fingerprint_hash: bytes,
            user_id: uuid.UUID
    ) -> bool:
        async with self.uow as uow:
            query = (
                select(UserSessionModel)
                .where(UserSessionModel.user_id == user_id)
                .where(UserSessionModel.fingerprint_hash == fingerprint_hash)
            )
            result = await uow.session.execute(query)
            return True if result.scalar_one_or_none() else False
    

    async def count_user_sessions(self: Self, user_id: uuid.UUID) -> int | None:
        async with self.uow as uow:
            count_query = (
                select(func.count(UserSessionModel.id))
                .where(UserSessionModel.user_id == user_id)
                )
            count_result = await uow.session.execute(count_query)
            return count_result.scalar()


    async def delete_user_session(
            self: Self,
            user_id: uuid.UUID,
            value: Any = None,
            delete_by: Optional[str] = None,
    ):
        async with self.uow as uow:
            if delete_by:
                delete_subquery = (
                    select(UserSessionModel.id)
                    .where(UserSessionModel.user_id == user_id)
                    .where(getattr(UserSessionModel, delete_by) == value)
                )
            else:
                delete_subquery = (
                    select(UserSessionModel.id)
                    .where(UserSessionModel.user_id == user_id)
                    .order_by(UserSessionModel.expire_at)
                    .limit(1)
                )
            delete_stmt = (
                delete(UserSessionModel)
                .where(UserSessionModel.id.in_(delete_subquery)))
            delete_result = await uow.session.execute(delete_stmt)
            await uow.session.flush()
            return delete_result.rowcount > 0


    async def delete_session_if_fingerprint_invalid(
            self: Self,
            user_id: uuid.UUID,
            refresh_token: str,
            fingerprint_hash: bytes
    ) -> bool:
        async with self.uow as uow:
            query = (
                select(
                    UserSessionModel.id,
                    UserSessionModel.fingerprint_hash,  
                )
                .where(UserSessionModel.user_id == user_id) 
                .where(UserSessionModel.refresh_token == refresh_token)
            )
            result = await uow.session.execute(query)
            query_result = result.first()
            if not query_result:
                raise MicroServiceError(detail='Что-то пошло не так')
            
            session_id, stored_fingerprint_hash = query_result
            if stored_fingerprint_hash != fingerprint_hash:
                delete_result = await uow.session.execute(
                    delete(UserSessionModel)
                    .where(UserSessionModel.id == session_id)
                )
                await uow.session.flush()
                return delete_result.rowcount > 0
            return False
              


class Container(containers.DeclarativeContainer):
    repository = providers.Factory(
        UserSessionRepositoryImpl,
        uow=Uow
    )

container = Container()

UserSessionRepository = container.repository

