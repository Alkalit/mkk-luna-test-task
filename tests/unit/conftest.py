import logging
import uuid
from collections.abc import AsyncIterator
from datetime import datetime as dt
from decimal import Decimal

import dishka_faststream as faststream_integration
import httpx
import pytest
import pytest_asyncio
from dishka import Provider, Scope, make_async_container, provide, AsyncContainer
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from fastapi import FastAPI
from fastapi.testclient import TestClient
from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitQueue, QueueType, TestRabbitBroker
from faststream.rabbit.publisher.usecase import RabbitPublisher
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)

from mkk.adapters.database.models import Payment as PaymentDBModel
from mkk.adapters.payment import AbstractPaymentClient, PaymentClient
from mkk.domain.models import Payment, Currency, Status
from mkk.infrastructure.logging import setup_logging
from mkk.infrastructure.resources.database import (
    setup_engine,
    setup_session,
    session_manager,
)
from mkk.presentation.web_api.payments import router
from mkk.presentation.consumers import amqp_router

logger = logging.getLogger(__name__)


class TestProvider(Provider):

    @provide(scope=Scope.APP)
    async def session(self) -> AsyncIterator[AsyncSession]:
        engine = create_async_engine(
            "postgresql+psycopg://mkk:mkk@postgresql/mkk",
        )
        session_factory = async_sessionmaker(
            autocommit=False, autoflush=False, bind=engine
        )
        session = session_factory()
        yield session
        await session.close()

    @provide(scope=Scope.APP)
    def payment_client(self) -> AbstractPaymentClient:
        return PaymentClient()

    @provide(scope=Scope.APP)
    async def http_client(self) -> AsyncIterator[httpx.AsyncClient]:
        async with httpx.AsyncClient() as client:
            yield client

    @provide(scope=Scope.APP)
    async def broker(self) -> AsyncIterator[RabbitBroker]:
        async with RabbitBroker(url="amqp://luna:rabbit123@rabbitmq:5672/") as _broker:
            _broker.include_router(amqp_router)
            async with TestRabbitBroker(_broker, with_real=True) as test_broker:
                yield test_broker


@pytest_asyncio.fixture(scope='session')
async def container() -> AsyncIterator[AsyncContainer]:
    yield make_async_container(TestProvider(), FastapiProvider())
    return


@pytest_asyncio.fixture(scope="session")
async def app(queue, container) -> AsyncIterator[FastAPI]:
    setup_logging()


    broker = await container.get(RabbitBroker)
    faststream_integration.setup_dishka(container, app=FastStream(broker))

    test_app = FastAPI()
    test_app.include_router(router)
    setup_dishka(container, test_app)

    yield test_app
    await container.close()

@pytest_asyncio.fixture(scope='session')
async def session(container: AsyncContainer) -> AsyncIterator[AsyncSession]:
    ses = await container.get(AsyncSession)
    yield ses
    return


@pytest.fixture
def client(app) -> TestClient:
    test_client = TestClient(app)
    return test_client


@pytest.fixture(scope="session")
def queue() -> RabbitQueue:
    queue = RabbitQueue(
        "payments.new",
        queue_type=QueueType.QUORUM,
        durable=True,
    )

    return queue


@pytest.fixture()
def pending_payment() -> Payment:
    return Payment(
        amount=Decimal(100),
        currency=Currency.RUB,
        description="test descr",
        status=Status.PENDING,
        idempotency_key=uuid.MAX,
        webhook_url="https://www.example.org/",
        meta={},
        created_at=dt.now(),
    )


@pytest_asyncio.fixture()
async def pending_payment_db_model(
        session: AsyncSession,
        pending_payment: Payment,
) -> PaymentDBModel:
    model = PaymentDBModel(
        amount=pending_payment.amount,
        currency=pending_payment.currency,
        description=pending_payment.description,
        status=pending_payment.status,
        idempotency_key=pending_payment.idempotency_key,
        webhook_url=pending_payment.webhook_url,
        meta=pending_payment.meta,
        created_at=pending_payment.created_at,
    )

    session.add(model)
    await session.flush()
    return model


@pytest_asyncio.fixture()
async def http_200() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, content="Well done")
            )
    ) as client:
        yield client


@pytest_asyncio.fixture()
async def http_500() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(500, content="Shit happend")
            )
    ) as client:
        yield client


@pytest_asyncio.fixture()
async def http_exception() -> AsyncIterator[httpx.AsyncClient]:
    def handler(request: httpx.Request):
        raise httpx.HTTPError("The speed of light has been exceeded!")

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        yield client
