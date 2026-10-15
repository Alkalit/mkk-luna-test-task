from mkk.adapters.payment import PaymentClient


class TestPaymentClient:

    def test_processing(self, default_payment):
        client = PaymentClient()
        client.do_processing(default_payment)  # should not raise
