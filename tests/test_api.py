import pytest
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mkk.adapters.database.models import Payment
from mkk.domain.models import Status, Currency
from decimal import Decimal


@pytest.mark.asyncio
class TestPaymentsCreation:

    async def test_simple_creation(self, client: TestClient, session: AsyncSession):
        response: Response = client.post(
            "/api/v1/payments",
            json=dict(
                amount="500.35",
                currency=Currency.EUR,
                description='Test desc',
                meta=dict(spam=1, ham=2, eggs=3),
                url='wss://domain/do-stuff',
            ),
            headers={"Idempotency-Key": "deadbeef-2e15-11f1-b0bb-02420a0a0102"}
        )

        payment_id = response.json()["payment_id"]

        assert response.status_code == 202
        assert bool(payment_id)
        assert response.json()["status"] == Status.PENDING
        assert bool(response.json()["created_at"])

        expression = select(Payment).filter_by(id=payment_id)
        payment: Payment = (await session.scalars(expression)).one()

        assert payment.amount == Decimal("500.35")
        assert payment.currency == Currency.EUR
        assert payment.description == 'Test desc'
        assert payment.meta == dict(spam=1, ham=2, eggs=3)
        assert payment.url == 'wss://domain/do-stuff'
        assert bool(payment.created_at)
        assert payment.processed_at is None
