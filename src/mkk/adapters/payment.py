__all__ = ["AbstractPaymentClient", "PaymentClient"]

import random
from abc import ABC

from mkk.domain.models import Payment


class AbstractPaymentClient(ABC):

    def __init__(self):
        pass

    def do_process(self, payment: Payment) -> bool:
        raise NotImplementedError


class PaymentClient(AbstractPaymentClient):
    """
    Pretends payment processing. Succeeds in 90% cases.
    """

    def do_processing(self, payment: Payment) -> bool:
        case = random.random()

        return case < 0.9
