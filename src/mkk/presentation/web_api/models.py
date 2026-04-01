from decimal import Decimal

from pydantic import BaseModel, JsonValue, WebsocketUrl

from mkk.domain.models import Currency


class PaymentCreation(BaseModel):
    amount: Decimal
    currency: Currency
    description: str = 'Test descr'
    meta: JsonValue
    url: WebsocketUrl
