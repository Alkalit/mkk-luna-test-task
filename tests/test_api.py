import pytest
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import select

from mkk.adapters.database.models import Payment
from mkk.domain.models import Status


@pytest.mark.asyncio
class TestPaymentsCreation:

    async def test_qwe(self, client: TestClient, session):
        response: Response = client.post("/api/v1/payments")

        assert response.status_code == 202
        assert bool(response.json()["payment_id"])
        assert response.json()["status"] == Status.SUCCEEDED
        assert response.json()["created_at"] == "1234"

        expression = select(Payment).where()
        result = (await session.execute(expression)).all()
        assert bool(result)
        assert len(result) == 1
