from fastapi import APIRouter, Response, status
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession, async_sessionmaker
from datetime import datetime as dt
from uuid import uuid1

from mkk.adapters.database.models import Payment, Currency, Status


payment_router = APIRouter()

async def eng() -> AsyncEngine:
    engine = create_async_engine(
        "postgresql+psycopg://mkk:mkk@postgresql/mkk",
    )
    return engine


async def ses(engine: AsyncEngine) -> AsyncSession:
    async with engine.connect() as connection:
        async with connection.begin():
            session_factory = async_sessionmaker()
            session = session_factory(bind=connection, join_transaction_mode="create_savepoint")
            yield session
            await session.close()



@payment_router.post("/api/v1/payments")
async def payments(response: Response):
    response.status_code = status.HTTP_202_ACCEPTED
    engine = await eng()
    async with engine.connect() as connection:
        async with connection.begin():
            session_factory = async_sessionmaker()
            session = session_factory(bind=connection, join_transaction_mode="create_savepoint")
            payment = Payment(
                amount=1,
                currency = Currency.RUB,
                description= 'text',
                status=Status.SUCCEEDED,
                url='test',
                meta={"spam": "ham"},
                created_at=dt.now(),
                idempotency_key=uuid1(),
            )
            session.add(payment)
            await session.commit()
            await session.close()
    return {"payment_id": "1234", "status": Status.SUCCEEDED, "created_at": "1234"}


@payment_router.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
