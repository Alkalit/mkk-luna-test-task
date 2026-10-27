from typing import AsyncIterator

import httpx
from dishka import Provider, provide, Scope
from faststream.rabbit import RabbitBroker, TestRabbitBroker, RabbitPublisher, RabbitQueue, QueueType
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from mkk.adapters.payment import AbstractPaymentClient, PaymentClient
from mkk.infrastructure.resources.database import setup_engine, setup_session, session_manager
from mkk.presentation.consumers import amqp_router


class MainProvider(Provider):

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
