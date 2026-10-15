__all__ = ["Currency", "Status", "Payment"]

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Json, Field, PositiveInt


class Currency(StrEnum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"


class Status(StrEnum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class Payment(BaseModel):
    id: PositiveInt
    amount: Decimal = Field(
        gt=0,
        max_digits=15,
        decimal_places=6,  # common default in finances.
    )
    currency: Currency
    description: str = Field(max_length=500)
    status: Status
    idempotency_key: UUID
    webhook_url: str
    meta: Json[dict]
    created_at: datetime
    processed_at: datetime
