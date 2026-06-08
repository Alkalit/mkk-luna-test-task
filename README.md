# Example of usage

Starting the echo server to listen for the payment processing results.

`python echo-server.py`

Sending a payment info.

```bash
curl -X POST \
-H "Idempotency-Key: ffffffff-ffff-ffff-ffff-ffffffffffff" \
-H "Content-Type: application/json" \
-d '{"amount":"500.35","currency":"EUR","description":"Test desc","meta":{"spam":1,"ham":2,"eggs":3},"url":"http://localhost:8000/api/v1/echo"}' \
http://localhost:8000
```

Then we wait for a few seconds for the result to come to the echo-server. Something like:

```
```