from contextlib import asynccontextmanager
from typing import Callable, AsyncIterator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
    AsyncSession,
)


def setup_engine() -> AsyncEngine:
    engine = create_async_engine(
        "postgresql+psycopg://mkk:mkk@postgresql/mkk",
    )
    return engine


def setup_session(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    session_factory = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return session_factory


@asynccontextmanager
async def session_manager(
        session_factory: Callable[[], AsyncSession],
) -> AsyncIterator[AsyncSession]:
    session = session_factory()
    try:
        yield session
    finally:
        await session.close()
