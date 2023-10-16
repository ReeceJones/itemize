import asyncio

import itemize.models as models

from itemize.config import CONFIG

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    async_scoped_session,
)


class DB:
    engine = create_async_engine(CONFIG.DB_URI, echo=CONFIG.ECHO_SQL, future=True)
    session_maker = async_sessionmaker(
        bind=engine, autoflush=False, expire_on_commit=False
    )
    async_session = async_scoped_session(session_maker, scopefunc=asyncio.current_task)

    @staticmethod
    async def init_db() -> None:
        async with DB.engine.begin() as conn:
            if CONFIG.TABLE_DROP_ON_STARTUP:
                await conn.run_sync(models.Base.metadata.drop_all)
            if CONFIG.TABLE_CREATE_ON_STARTUP:
                await conn.run_sync(models.Base.metadata.create_all)
