from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from mkk.presentation.web_api.payments import payment_router
from mkk.infrastructure.database import setup_engine, setup_session, session_manager


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(payment_router)
    engine = setup_engine()
    session_factory = setup_session(engine)

    # Dependency injection.
    app.dependency_overrides[AsyncSession] = session_manager(session_factory)
    return app


app = create_app()
