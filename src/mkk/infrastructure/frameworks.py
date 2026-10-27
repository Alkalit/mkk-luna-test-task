from fastapi import FastAPI
from mkk.presentation.web_api.payments import router

def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app
