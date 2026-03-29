from fastapi import APIRouter, Response, status
from mkk.domain.models import Status


payment_router = APIRouter()


@payment_router.post("/api/v1/payments")
async def payments(response: Response):
    response.status_code = status.HTTP_202_ACCEPTED
    return {"payment_id": "1234", "status": Status.SUCCEEDED, "created_at": "1234"}


@payment_router.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
