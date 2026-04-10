import pytest
from faststream.rabbit import TestRabbitBroker

from conftest import broker
from mkk.presentation.amqp import router


@router.subscriber('testout')
async def testout_handle(data: int):
    return 'qwerty'


@pytest.mark.asyncio
async def test_handle(broker):
    async with TestRabbitBroker(broker, with_real=True) as test_broker:
        await test_broker.publish(0, queue="testout")
        await testout_handle.wait_call(timeout=3)
        testout_handle.mock.assert_called_once_with(0)
