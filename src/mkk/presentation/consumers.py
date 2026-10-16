from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mkk.domain.models import Status
from mkk.adapters.database.models import Payment as PaymentDB
from mkk.adapters.payment import AbstractPaymentClient


async def payment_processing(
        payment_id: int,
        session: AsyncSession,
        payment_client: AbstractPaymentClient,
        http_client,
):
    expression = select(PaymentDB).filter_by(id=payment_id)
    payment: PaymentDB = (await session.scalars(expression)).one()
    payment.status = Status.SUCCEEDED
    session.add(payment)
    await session.flush()
    await session.commit()
