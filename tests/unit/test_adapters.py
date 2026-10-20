from mkk.adapters.payment import PaymentClient


class TestPaymentClient:

    def test_processing(self, pending_payment):
        client = PaymentClient()
        client.do_processing(pending_payment)  # should not raise
