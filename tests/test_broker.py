import pytest

from decimal import Decimal
from datetime import datetime as dt
from uuid import uuid8

from faststream.rabbit import RabbitBroker
from faststream.rabbit import TestRabbitBroker

from mkk.domain.models import Payment, Currency, Status


class TestStatusChecker:

    @pytest.mark.asyncio
    async def test_smth(self,
                        broker: RabbitBroker,
                        queue,
                        ):
        async with TestRabbitBroker(broker, with_real=True) as test_broker:
            payment = Payment(  # dataclass
                id=10,
                amount=Decimal('100'),
                currency=Currency.EUR,
                description='test description',
                status=Status.PENDING,
                url='wss://domain.com/websocket-handler/',
                meta={},
                created_at=dt.now(),
                processed_at=dt.now(),
                idempotency_key=uuid8(),
            )
            await test_broker.publish(
                payment,
                queue=queue,
            )

# @router.subscriber('testout')
# async def testout_handle(data: int):
#     return 'qwerty'
#
#
# @pytest.mark.asyncio
# async def test_handle(broker):
#     async with TestRabbitBroker(broker, with_real=True) as test_broker:
#         await test_broker.publish(0, queue="testout")
#         await testout_handle.wait_call(timeout=3)
#         testout_handle.mock.assert_called_once_with(0)
