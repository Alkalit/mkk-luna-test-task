from faststream.rabbit.fastapi import RabbitBroker
from faststream.security import SASLPlaintext

from faststream.rabbit import RabbitBroker

def new_broker() -> RabbitBroker:
    return RabbitBroker(
        host="rabbitmq",
        port=5672,
        security=SASLPlaintext(
            username="luna",
            password="rabbit123",
        ),

        virtualhost="/",
    )