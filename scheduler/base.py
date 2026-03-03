from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import settings

jobs_scheduler = AsyncIOScheduler(jobstores={"default": SQLAlchemyJobStore(url=settings.jobs_store_db_url)})
