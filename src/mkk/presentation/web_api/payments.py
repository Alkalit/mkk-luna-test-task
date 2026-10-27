import logging
from datetime import datetime as dt

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, Header, HTTPException, status
from faststream.rabbit import RabbitPublisher
from faststream.rabbit import RabbitQueue, QueueType
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from mkk.adapters.database.models import Payment as PaymentDB, Status
from mkk.domain.models import Payment
from mkk.presentation.web_api.models import (
    PaymentCreation,
    PaymentCreationHeaders,
    PaymentCreationInfo,
)

router = APIRouter(route_class=DishkaRoute)

logger = logging.getLogger(__name__)

queue = RabbitQueue(
    "payments.new",
    queue_type=QueueType.QUORUM,
    durable=True,
)


@router.post("/api/v1/payments", status_code=202)
async def create_payment(
        payment_data: PaymentCreation,
        session: FromDishka[AsyncSession],
        publisher: FromDishka[RabbitPublisher],
        headers: PaymentCreationHeaders = Header(),

) -> PaymentCreationInfo:
    payment = PaymentDB(
        amount=payment_data.amount,
        currency=payment_data.currency,
        description=payment_data.description,
        status=Status.PENDING,
        webhook_url=str(payment_data.url),
        meta=payment_data.meta,
        created_at=dt.now(),
        idempotency_key=headers.idempotency_key,
    )
    session.add(payment)
    await session.flush()

    data = PaymentCreationInfo(
        payment_id=payment.id,
        status=payment.status,
        created_at=payment.created_at,
    )

    await publisher.publish(payment.id, queue=queue, content_type='text/plain')

    await session.commit()
    return data


@router.get("/api/v1/payments/{payment_id}")
async def get_payment(
        payment_id: int,
        session: AsyncSession = Depends(),
) -> Payment:
    expression = select(PaymentDB).filter_by(id=payment_id)
    try:
        payment: PaymentDB = (await session.scalars(expression)).one()
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )

    return payment
