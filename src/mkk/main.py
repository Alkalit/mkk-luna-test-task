import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import dishka_faststream as faststream_integration
import uvicorn
from dishka import make_async_container
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from fastapi import FastAPI
from faststream import FastStream
from faststream.rabbit import RabbitBroker

from mkk.infrastructure.frameworks import create_app
from mkk.infrastructure.ioc import MainProvider
from mkk.infrastructure.logging import setup_logging


@asynccontextmanager
async def setup_app() -> AsyncGenerator[FastAPI, None]:
    setup_logging()

    container = make_async_container(MainProvider(), FastapiProvider())

    _app = create_app()
    setup_dishka(container, _app)

    faststream_integration.setup_dishka(container, app=FastStream(await container.get(RabbitBroker)))

    yield _app

    await container.close()


async def main() -> None:
    async with setup_app() as app:
        server = uvicorn.Server(
            uvicorn.Config(app, host="0.0.0.0", port=8000)
        )
        await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
