from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from config import settings


engine = create_async_engine(url=settings.db_url)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession)


async def get_db_session(with_commit=True) -> AsyncGenerator[AsyncSession | Any, Any]:
    async with async_session_maker() as session:
        try:
            yield session
            if with_commit:
                await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
