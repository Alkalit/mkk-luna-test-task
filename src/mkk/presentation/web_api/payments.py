from datetime import datetime as dt
from uuid import uuid1

from fastapi import APIRouter, Response, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from mkk.adapters.database.models import Payment, Currency, Status

payment_router = APIRouter()


@payment_router.post("/api/v1/payments")
async def payments(
        response: Response,
        session: AsyncSession = Depends(AsyncSession),
):
    print('came here!!!!!!!!!!!!')
    response.status_code = status.HTTP_202_ACCEPTED
    payment = Payment(
        amount=1,
        currency=Currency.RUB,
        description='text',
        status=Status.SUCCEEDED,
        url='test',
        meta={"spam": "ham"},
        created_at=dt.now(),
        idempotency_key=uuid1(),
    )
    session.add(payment)
    await session.commit()
    return {"payment_id": "1234", "status": Status.SUCCEEDED, "created_at": "1234"}


@payment_router.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
