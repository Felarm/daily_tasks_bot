from loguru import logger
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import create_async_engine

from config import settings
from db.database import Base


async def create_db_if_not_exists():
    admin_url = settings.db_url[:-len(settings.DB_NAME)] + "postgres"
    db_creation_engine = create_async_engine(url=admin_url, isolation_level="AUTOCOMMIT")
    async with db_creation_engine.begin() as conn:
        try:
            await conn.execute(text(f"CREATE DATABASE {settings.DB_NAME}"))
            await conn.execute(text(f"CREATE DATABASE jobs"))
            logger.info(f"created db {settings.DB_NAME} and db for jobs")
        except ProgrammingError:
            logger.info(f"db {settings.DB_NAME} already exists")
    await db_creation_engine.dispose()


async def init_db():
    await create_db_if_not_exists()
    tables_creation_engine = create_async_engine(url=settings.db_url)
    async with tables_creation_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info(f"created tables: {Base.metadata.tables}")
    await tables_creation_engine.dispose()
