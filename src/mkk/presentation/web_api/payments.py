from datetime import datetime as dt

from fastapi import APIRouter, Response, status, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from mkk.adapters.database.models import Payment, Status
from mkk.presentation.web_api.models import PaymentCreation, PaymentCreationHeader

payment_router = APIRouter()


@payment_router.post("/api/v1/payments")
async def payments(
        response: Response,
        payment_data: PaymentCreation,
        session: AsyncSession = Depends(),
        headers: PaymentCreationHeader = Header(),
):

    response.status_code = status.HTTP_202_ACCEPTED
    created_at = dt.now()
    payment = Payment(
        amount=payment_data.amount,
        currency=payment_data.currency,
        description=payment_data.description,
        status=Status.PENDING,
        url=str(payment_data.url),
        meta=payment_data.meta,
        created_at=created_at,
        idempotency_key=headers.idempotency_key,
    )
    session.add(payment)
    await session.flush()
    data = {
        "payment_id": payment.id,
        "status": payment.status,
        "created_at": created_at,
    }

    await session.commit()
    return data


@payment_router.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
