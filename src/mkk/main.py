from fastapi import FastAPI
from faststream import FastStream
from sqlalchemy.ext.asyncio import AsyncSession

from mkk.infrastructure.resources.database import setup_engine, setup_session, session_manager
from mkk.infrastructure.resources.broker import new_broker
from mkk.presentation.web_api.payments import payment_router
from mkk.presentation.amqp import router


def create_faststream_app() -> FastStream:
    broker = new_broker()
    faststream_app = FastStream(broker)
    broker.include_router(router)

    return faststream_app


def create_fastapi_app() -> FastAPI:
    fastapi_app = FastAPI()
    fastapi_app.include_router(payment_router)

    return fastapi_app


def create_app() -> FastAPI:
    engine = setup_engine()
    session_factory = setup_session(engine)

    faststream_app = create_faststream_app()
    fastapi_app = create_fastapi_app()

    fastapi_app.add_event_handler("startup", faststream_app.broker.start)
    fastapi_app.add_event_handler("shutdown", faststream_app.broker.close)

    # Dependency injection.
    fastapi_app.dependency_overrides[AsyncSession] = session_manager(session_factory)
    return fastapi_app


app = create_app()