from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import settings
from db.session import get_db_session
from notifier.dao import UserNotifierSettingsDao
from notifier.models import UserNotifierSettings
from notifier.schemas import UpdatedSettings

jobs_scheduler = AsyncIOScheduler(jobstores={"default": SQLAlchemyJobStore(url=settings.jobs_store_db_url)})


class UserNotifierSettingsService:
    @staticmethod
    async def get_user_settings(user_id: int) -> UserNotifierSettings | None:
        async with get_db_session(False) as session:
            return await UserNotifierSettingsDao(session).get_user_settings(user_id)

    @staticmethod
    async def update_user_settings(user_id: int, new_values: UpdatedSettings) -> UserNotifierSettings | None:
        async with get_db_session() as session:
            return await UserNotifierSettingsDao(session).update_user_settings(user_id, new_values.model_dump())