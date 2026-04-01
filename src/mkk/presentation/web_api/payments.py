from typing import Annotated
from decimal import Decimal
from pydantic import BaseModel, Field, Json, WebsocketUrl, JsonValue
from datetime import datetime as dt
from uuid import uuid1

from fastapi import APIRouter, Response, status, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession

from mkk.adapters.database.models import Payment, Currency, Status

payment_router = APIRouter()


class PaymentCreation(BaseModel):
    amount: Decimal
    currency: Currency
    description: str = 'Test descr'
    meta: JsonValue
    url: WebsocketUrl


@payment_router.post("/api/v1/payments")
async def payments(
        response: Response,
        payment_data: PaymentCreation,
        session: AsyncSession = Depends(),
):

    response.status_code = status.HTTP_202_ACCEPTED
    created_at = dt.now()
    payment = Payment(
        amount=payment_data.amount,
        currency=payment_data.currency,
        description=payment_data.description,
        status=Status.PENDING,
        url=str(payment_data.url), # NOQA
        meta=payment_data.meta,
        created_at=created_at,
        idempotency_key=uuid1(),  # TODO
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
