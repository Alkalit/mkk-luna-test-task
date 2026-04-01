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
        assert response.json() == {"payment_id": "1234", "status": Status.SUCCEEDED, "created_at": "1234"}

        expression = select(Payment)
        result = (await session.execute(expression)).all()
        print(result)
        assert bool(result)
