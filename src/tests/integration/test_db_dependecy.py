# from contextlib import asynccontextmanager
# from typing import Any, AsyncGenerator
# from sqlalchemy.ext.asyncio import (
#     async_sessionmaker,
#     create_async_engine,
#     AsyncSession
# )
# from config import settings


# engine = create_async_engine(
#     url=settings.db.test_postgres_dsn
# )

# async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=True)


# async def get_test_db_session() -> AsyncGenerator[AsyncSession, Any]:
#     async with async_session_maker() as session:
#         yield session


# @asynccontextmanager
# async def provide_test_session():
#     async for session in get_test_db_session():  
#         yield session
