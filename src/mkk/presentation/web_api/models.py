from decimal import Decimal

from pydantic import BaseModel, JsonValue, AnyHttpUrl, Field, UUID1
from datetime import datetime

from mkk.domain.models import Currency, Status


class PaymentCreation(BaseModel):
    amount: Decimal
    currency: Currency
    description: str
    meta: JsonValue
    url: AnyHttpUrl


class PaymentCreationHeaders(BaseModel):
    idempotency_key: UUID1 = Field()


class PaymentCreationInfo(BaseModel):
    payment_id: int
    status: Status
    created_at: datetime
