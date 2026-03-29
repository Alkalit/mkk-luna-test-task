import pytest

from fastapi.testclient import TestClient
from httpx import Response

from mkk.domain.models import Status


def test_qwe(client: TestClient):
    response: Response = client.post("/api/v1/payments")
    assert response.status_code == 202
    assert response.json() == {"payment_id": "1234", "status": Status.SUCCEEDED, "created_at": "1234"}
