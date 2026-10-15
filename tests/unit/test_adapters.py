import uuid
from datetime import datetime as dt
from decimal import Decimal
from mkk.adapters.payment import PaymentClient
from mkk.domain.models import Payment, Currency, Status


class TestPaymentClient:

    def test_processing(self):
        client = PaymentClient()
        payment = Payment(
            id=1,
            amount=Decimal(100),
            currency=Currency.RUB,
            description='test descr',
            status=Status.PENDING,
            idempotency_key=uuid.MAX,
            webhook_url='https://domain.com',
            meta={},
            created_at=dt.now(),
            processed_at=dt.now(),
        )
        client.do_processing(payment)  # should not raise
