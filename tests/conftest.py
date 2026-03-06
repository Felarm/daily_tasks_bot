from datetime import datetime, timedelta

import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine

from daily_task.dao import DailyTaskDao
from daily_task.models import DailyTask
from user.dao import UserDao
from db.database import Base
from user.models import User

TEST_DB_URL = "sqlite+aiosqlite:///:memory"


@pytest_asyncio.fixture(scope="session")
async def engine() -> AsyncEngine:
    engine = create_async_engine(url=TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        # create tables in test db
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        # drop tables in test db
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def session(engine) -> AsyncSession:
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        await session.begin()
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def daily_task_user(session) -> User:
    test_user = await UserDao(session).new_user(username="test_user")
    return test_user


@pytest_asyncio.fixture(scope="function")
async def present_daily_task(session, daily_task_user) -> DailyTask:
    return await DailyTaskDao(session).create_user_daily_task(
        user_id=daily_task_user.id,
        name="conftest_daily_task",
        start_dt=datetime.now(),
        end_dt=datetime.now() + timedelta(seconds=5)
    )