import logging
from datetime import datetime as dt

from fastapi import APIRouter, Depends, Header, HTTPException
from faststream.rabbit.publisher.usecase import RabbitPublisher
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from mkk.adapters.database.models import Payment as PaymentDB, Status
from mkk.domain.models import Payment
from mkk.presentation.web_api.models import PaymentCreation, PaymentCreationHeaders, PaymentCreationInfo

payment_router = APIRouter()

logger = logging.getLogger(__name__)


@payment_router.post("/api/v1/payments", status_code=202)
async def create_payment(
        payment_data: PaymentCreation,
        headers: PaymentCreationHeaders = Header(),
        session: AsyncSession = Depends(),
        publisher: RabbitPublisher = Depends(),
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

    await publisher.publish('payment proc')

    await session.commit()
    return data


@payment_router.get("/api/v1/payments/{payment_id}")
async def get_payment(
        payment_id: int,
        session: AsyncSession = Depends(),
) -> Payment:

    expression = select(PaymentDB).filter_by(id=payment_id)
    try:
        payment: PaymentDB = (await session.scalars(expression)).one()
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Item not found')

    return payment
