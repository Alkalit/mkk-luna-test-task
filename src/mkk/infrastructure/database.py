from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, AsyncSession

def setup_engine() -> AsyncEngine:
    engine = create_async_engine(
        "postgresql+psycopg://mkk:mkk@postgresql/mkk",
    )
    return engine

def setup_session(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    session_factory = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return session_factory
