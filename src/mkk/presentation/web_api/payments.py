from datetime import datetime as dt

from fastapi import APIRouter, Response, status, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from mkk.adapters.database.models import Payment as PaymentDB, Status
from mkk.domain.models import Payment
from mkk.presentation.web_api.models import PaymentCreation, PaymentCreationHeaders, PaymentCreationInfo

payment_router = APIRouter()


@payment_router.post("/api/v1/payments")
async def create_payment(
        response: Response,
        payment_data: PaymentCreation,
        headers: PaymentCreationHeaders = Header(),
        session: AsyncSession = Depends(),
) -> PaymentCreationInfo:
    response.status_code = status.HTTP_202_ACCEPTED
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
