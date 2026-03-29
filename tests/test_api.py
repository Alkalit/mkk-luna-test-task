import pytest

from fastapi.testclient import TestClient
from httpx import Response


def test_qwe(client: TestClient):
    response: Response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
