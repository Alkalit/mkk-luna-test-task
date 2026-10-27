import logging
import uuid
from collections.abc import AsyncIterator, Iterator
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
from faststream.rabbit import RabbitBroker, RabbitQueue, QueueType, TestRabbitBroker, RabbitPublisher
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
)

from mkk.adapters.database.models import Payment as PaymentDBModel
from mkk.adapters.payment import AbstractPaymentClient, PaymentClient
from mkk.domain.models import Payment, Currency, Status
from mkk.infrastructure.frameworks import create_app
from mkk.infrastructure.logging import setup_logging
from mkk.infrastructure.resources.database import (
    setup_engine,
    setup_session,
    session_manager,
)
from mkk.presentation.consumers import amqp_router

logger = logging.getLogger(__name__)


class TestProvider(Provider):

    @provide(scope=Scope.APP)
    def engine(self) -> AsyncEngine:
        return setup_engine()

    @provide(scope=Scope.APP)
    async def session(self, engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
        factory = setup_session(engine)
        async with session_manager(factory) as _session:
            yield _session

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
            async with TestRabbitBroker(_broker) as test_broker:
                yield test_broker

    @provide(scope=Scope.REQUEST)
    def publisher(self, broker: RabbitBroker) -> RabbitPublisher:
        _publisher = broker.publish()

        queue = RabbitQueue(
            "payments.new",
            queue_type=QueueType.QUORUM,
            durable=True,
        )
        return broker.publisher(queue)


@pytest_asyncio.fixture(scope='session')
async def container() -> AsyncIterator[AsyncContainer]:
    _container = make_async_container(TestProvider(), FastapiProvider())
    yield _container
    await _container.close()


@pytest_asyncio.fixture(scope="session")
async def app(container) -> AsyncIterator[FastAPI]:
    setup_logging()

    _app = create_app()
    setup_dishka(container, _app)

    faststream_integration.setup_dishka(container, app=FastStream(await container.get(RabbitBroker)))

    yield _app


@pytest_asyncio.fixture(scope='session')
async def session(container: AsyncContainer) -> AsyncIterator[AsyncSession]:
    ses = await container.get(AsyncSession)
    yield ses
    return


@pytest.fixture
def client(app) -> TestClient:
    test_client = TestClient(app)
    return test_client


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
