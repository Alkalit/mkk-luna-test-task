import uuid
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mkk.adapters.database.models import Payment
from mkk.domain.models import Status, Currency


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
                url='https://domain/do-stuff',
            ),
            headers={
                "Idempotency-Key": str(uuid.uuid1()),
            }
        )

        data = response.json()

        assert response.status_code == 202
        assert bool(data['payment_id'])
        assert response.json()["status"] == Status.PENDING
        assert bool(response.json()["created_at"])

        expression = select(Payment).filter_by(id=data['payment_id'])
        payment: Payment = (await session.scalars(expression)).one()

        assert payment.amount == Decimal("500.35")
        assert payment.currency == Currency.EUR
        assert payment.description == 'Test desc'
        assert payment.meta == dict(spam=1, ham=2, eggs=3)
        assert payment.webhook_url == 'https://domain/do-stuff'
        assert bool(payment.created_at)
        assert payment.processed_at is None

    async def test_check_message_sending(self, client: TestClient, session: AsyncSession):
        pass


@pytest.mark.asyncio
class TestPaymentsInfo:

    def test_if_payment_doesnt_exist(self, client: TestClient, session: AsyncSession):
        response: Response = client.get(
            "/api/v1/payments/42",
        )

        assert response.status_code == 404

    def test_get_payment_info(self, client: TestClient, session: AsyncSession):
        response: Response = client.get(
            "/api/v1/payments/1",
        )

        assert response.status_code == 200
        assert response.json() == {'id': 1, 'amount': '500.35', 'currency': 'EUR', 'description': 'Test desc',
                                   'status': 'pending', 'idempotency_key': '0e703ebc-c956-11f1-b92a-02420a0a0104',
                                   'webhook_url': 'https://domain/do-stuff', 'meta': {'ham': 2, 'eggs': 3, 'spam': 1},
                                   'created_at': '2026-10-16T11:38:07.182080', 'processed_at': None}
