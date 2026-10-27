import uuid
import pytest
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mkk.adapters.database.models import Payment
from mkk.domain.models import Status, Currency
from decimal import Decimal

host = "localhost:3000"
mock_server = "localhost:4000"


class TestPaymentProcessing:

    async def test_successful_payment_workflow(
        self, client: TestClient, session: AsyncSession
    ):
        # create a payment
        response: Response = client.post(
            "/api/v1/payments",
            json=dict(
                amount="500.35",
                currency=Currency.EUR,
                description="Test desc",
                meta=dict(spam=1, ham=2, eggs=3),
                url="https://domain/do-stuff",
            ),
            headers={
                "Idempotency-Key": str(uuid.uuid1()),
            },
        )

        data = response.json()

        # check db - payment has succeeded
        expression = select(Payment).filter_by(id=data["payment_id"])
        payment: Payment = (await session.scalars(expression)).one()
        assert payment.status == Status.SUCCEEDED

        # webhook got called
        ...

    def test_failed_payment_workflow(self):
        # create a payment
        # webhook did not get called
        # check db - payment has failed
        # check DLQ
        ...
