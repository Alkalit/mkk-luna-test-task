from collections.abc import Generator

import httpx
import pytest
from sqlalchemy import select

from mkk.adapters.database.models import Payment as PaymentDB
from mkk.adapters.payment import AbstractPaymentClient
from mkk.domain.models import Payment, Status
from mkk.presentation.consumers import payment_processing


class SucceedingPaymentClient(AbstractPaymentClient):

    def do_process(self, payment: Payment) -> bool:
        return True


class FailingPaymentClient(AbstractPaymentClient):

    def do_process(self, payment: Payment) -> bool:
        return False


@pytest.fixture()
def succeeding_client() -> SucceedingPaymentClient:
    return SucceedingPaymentClient()


@pytest.fixture()
def failing_client() -> FailingPaymentClient:
    return FailingPaymentClient()


@pytest.fixture()
def http_client() -> Generator[httpx.Client]:
    with httpx.Client() as client:
        yield client


# Test:
# successful payment
# failed payment
# web hook notification if any
class TestPaymentProcessingConsumer:

    @pytest.mark.asyncio
    async def test_successful_payment(self,
                                      session,
                                      succeeding_client,
                                      http_client,
                                      pending_payment_db_model,
                                      ):

        id = pending_payment_db_model.id

        await payment_processing(
            pending_payment_db_model.id,
            session,
            succeeding_client,
            http_client,
            # todo broker client
        )

        expression = select(PaymentDB).filter_by(id=id)
        payment: PaymentDB = (await session.scalars(expression)).one()

        assert payment.status == Status.SUCCEEDED

    @pytest.mark.asyncio
    async def test_failed_payment(self,
                                  session,
                                  failing_client,
                                  http_client,
                                  pending_payment_db_model,
                                  ):

        id = pending_payment_db_model.id

        await payment_processing(
            pending_payment_db_model.id,
            session,
            failing_client,
            http_client,
            # todo broker client
        )

        expression = select(PaymentDB).filter_by(id=id)
        payment: PaymentDB = (await session.scalars(expression)).one()

        assert payment.status == Status.FAILED
