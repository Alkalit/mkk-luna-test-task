from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID


class Currency(Enum):
    pass


class Status(Enum):
    pass


# JSON can be not only a js-object, but also an array and etc
#  but here we simplify
class JSON(dict):
    pass


@dataclass
class Payment:
    id: int
    amount: Decimal
    currency: Currency
    description: str
    status: Status
    idempotency_key: UUID
    url: str
    meta: JSON
    created_at: datetime
    updated_at: datetime
