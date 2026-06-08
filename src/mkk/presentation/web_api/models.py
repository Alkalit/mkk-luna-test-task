from decimal import Decimal

from pydantic import BaseModel, JsonValue, AnyHttpUrl, Field, UUID1

from mkk.domain.models import Currency


class PaymentCreation(BaseModel):
    amount: Decimal
    currency: Currency
    description: str
    meta: JsonValue
    url: AnyHttpUrl


class PaymentCreationHeader(BaseModel):
    idempotency_key: UUID1 = Field()
