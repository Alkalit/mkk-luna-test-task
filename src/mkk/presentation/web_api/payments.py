from fastapi import APIRouter


payment_router = APIRouter()


@payment_router.get("/")
async def root():
    return {"message": "Hello World"}


@payment_router.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
