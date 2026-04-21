import asyncio
import random

from faststream.rabbit import RabbitRouter, RabbitQueue

from mkk.domain.models import Payment

router = RabbitRouter()


@router.subscriber(RabbitQueue("payments.new", declare=False))
async def status_checker(
        payment: Payment,
) -> None:
    success = True

    await asyncio.sleep(random.uniform(2, 5))
    if random.random() < 0.1:
        success = False
