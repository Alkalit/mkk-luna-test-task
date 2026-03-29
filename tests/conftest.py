import asyncio

import pytest
from typing import Iterator
from fastapi import FastAPI
from fastapi.testclient import TestClient

from mkk.presentation.web_api.payments import payment_router


@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
def app() -> FastAPI:
    test_app = FastAPI()
    test_app.include_router(payment_router)
    return test_app


@pytest.fixture
def client(app) -> TestClient:
    test_client = TestClient(app)
    return test_client