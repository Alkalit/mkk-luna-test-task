import uuid
from datetime import datetime as dt
from decimal import Decimal

import pytest
from pydantic import ValidationError

from mkk.domain.models import Payment, Status, Currency


def test_simple_creation():
    # should not raise
    Payment(
        id=1,
        amount=Decimal(100),
        currency=Currency.RUB,
        description="test descr",
        status=Status.PENDING,
        idempotency_key=uuid.MAX,
        webhook_url="https://domain.com",
        meta="{}",
        created_at=dt.now(),
        processed_at=dt.now(),
    )


def test_cannot_create_a_negative_payments():
    with pytest.raises(ValidationError):
        Payment(
            id=1,
            amount=Decimal(-100),
            currency=Currency.RUB,
            description="test descr",
            status=Status.PENDING,
            idempotency_key=uuid.MAX,
            webhook_url="https://domain.com",
            meta="{}",
            created_at=dt.now(),
            processed_at=dt.now(),
        )
