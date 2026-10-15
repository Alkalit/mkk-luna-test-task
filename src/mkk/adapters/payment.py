__all__ = ['AbstractPaymentClient', 'PaymentClient']

from abc import ABC
import random
from mkk.domain.models import Payment


class AbstractPaymentClient(ABC):

    def __init__(self):
        pass

    def do_process(self, payment: Payment) -> bool:
        raise NotImplementedError


class PaymentClient(AbstractPaymentClient):
    """
    Эмулирует обработку платежа (2-5 сек, 90% успех, 10% ошибка)
    """

    def do_processing(self, payment: Payment) -> bool:
        case = random.random()

        return case < 0.9
