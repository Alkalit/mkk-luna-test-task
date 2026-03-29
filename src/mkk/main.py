from fastapi import FastAPI

from mkk.presentation.web_api.payments import payment_router


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(payment_router)

    return app


app = create_app()
