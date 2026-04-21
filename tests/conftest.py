import asyncio
from typing import Iterator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitQueue, QueueType
from faststream.security import SASLPlaintext
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession, async_sessionmaker

from mkk.infrastructure.resources.database import setup_engine, setup_session, session_manager
from mkk.presentation.amqp import router
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

    engine = setup_engine()
    session_factory = setup_session(engine)

    # Dependency injection.
    test_app.dependency_overrides[AsyncSession] = session_manager(session_factory)
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


@pytest.fixture(scope='session')
def queue() -> RabbitQueue:
    queue = RabbitQueue(
        'payments.new',
        queue_type=QueueType.QUORUM,
        durable=True,
    )

    return queue


@pytest.fixture(scope='session')
def broker(queue) -> RabbitBroker:

    broker = RabbitBroker(
        host="rabbitmq",
        port=5672,
        security=SASLPlaintext(
            username="luna",
            password="rabbit123",
        ),
        virtualhost="/",
    )
    broker.declare_queue(queue)
    broker.include_router(router)
    return broker


@pytest.fixture(scope='session')
async def amqp_app(broker: RabbitBroker) -> FastStream:
    app = FastStream(broker)
    return app
