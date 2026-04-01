import asyncio
from typing import Iterator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession, async_sessionmaker

from mkk.presentation.web_api.payments import payment_router


@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
def app() -> FastAPI:
    test_app = FastAPI()
    test_app.include_router(payment_router)
    return test_app


@pytest.fixture
def client(app) -> TestClient:
    test_client = TestClient(app)
    return test_client


@pytest_asyncio.fixture(scope='session')
async def engine() -> AsyncEngine:
    engine = create_async_engine(
        "postgresql+psycopg://mkk:mkk@postgresql/mkk",
    )
    return engine


@pytest_asyncio.fixture(scope="function")
async def session(engine: AsyncEngine) -> AsyncSession:
    async with engine.connect() as connection:
        async with connection.begin():
            session_factory = async_sessionmaker()
            session = session_factory(bind=connection, join_transaction_mode="create_savepoint")
            yield session
            await session.close()
