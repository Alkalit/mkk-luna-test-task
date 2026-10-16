from datetime import datetime as dt

from fastapi import APIRouter, Response, status, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from mkk.adapters.database.models import Payment, Status
from mkk.presentation.web_api.models import PaymentCreation, PaymentCreationHeaders
from mkk.presentation.web_api.models import PaymentCreationInfo

payment_router = APIRouter()


@payment_router.post("/api/v1/payments")
async def payments(
        response: Response,
        payment_data: PaymentCreation,
        headers: PaymentCreationHeaders = Header(),
        session: AsyncSession = Depends(),
) -> PaymentCreationInfo:

    response.status_code = status.HTTP_202_ACCEPTED
    payment = Payment(
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
