__all__ = ["amqp_router", "payment_processing"]

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

from faststream.rabbit import RabbitBroker, RabbitQueue, QueueType
from mkk.domain.models import Payment, Status
from mkk.adapters.database.models import Payment as PaymentDBModel
from mkk.adapters.payment import AbstractPaymentClient
from dishka_faststream import inject as faststream_inject

from faststream.rabbit import RabbitRouter

from dishka_faststream import (
    FromDishka,
)

queue = RabbitQueue(
    "payments.new",
    queue_type=QueueType.QUORUM,
    durable=True,
)

amqp_router = RabbitRouter()


@amqp_router.subscriber(queue)
@faststream_inject
async def payment_processing(
    payment_id: int,
    session: FromDishka[AsyncSession],
    payment_client: FromDishka[AbstractPaymentClient],
    http_client: FromDishka[AsyncClient],
) -> None:
    expression = select(PaymentDBModel).filter_by(id=payment_id)
    payment: PaymentDBModel = (await session.scalars(expression)).one()
    webhook_url = payment.webhook_url

    success = payment_client.do_process(
        Payment(
            id=payment.id,
            amount=payment.amount,
            currency=payment.currency,
            description=payment.description,
            status=payment.status,
            idempotency_key=payment.idempotency_key,
            webhook_url=payment.webhook_url,
            meta=payment.meta,
            created_at=payment.created_at,
        )
    )

    payment.status = Status.SUCCEEDED if success else Status.FAILED
    session.add(payment)
    await session.flush()
    await session.commit()

    await http_client.get(webhook_url)
