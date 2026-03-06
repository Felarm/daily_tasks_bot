from datetime import timedelta

from loguru import logger

from daily_task.models import DailyTask
from user.dao import UserDao
from user.models import NotifySettingsSchema

from db.session import get_db_session
from scheduler.base import jobs_scheduler
from scheduler.jobs import send_user_msg_job, start_user_dialog_job, end_user_dialog_job


class DailyTaskSchedulerService:
    def __init__(self, daily_task: DailyTask, user_id: int, chat_id: int):
        self.daily_task = daily_task
        self.user_id = user_id
        self.chat_id = chat_id

    async def add_tracker_jobs(self):
        await self.notify_before_task_start()
        self.run_task_start_dialog()
        self.run_task_end_dialog()

    async def notify_before_task_start(self):
        async with get_db_session(False) as session:
            task_user = await UserDao(session).get_one_or_none_by_id(self.user_id)
        if not task_user:
            logger.warning(f"user with user_id: {self.user_id} not found")
            return
        user_settings = NotifySettingsSchema(**task_user.notify_settings)
        if not user_settings.enabled:
            logger.warning(f"user {task_user.username} disabled notifications")
        for mins in user_settings.mins_before_dt_start:
            notify_text = (f"hello {task_user.username}\n"
                           f"task {self.daily_task.name} will start starts in {mins} minutes")
            notify_time = self.daily_task.start_dt - timedelta(minutes=mins)
            jobs_scheduler.add_job(
                func=send_user_msg_job,
                trigger="date",
                next_run_time=notify_time,
                replace_existing=True,
                kwargs={"user_id": self.user_id, "text": notify_text},
            )
            logger.debug(f"{task_user.username} should receive notification about task {self.daily_task.name} begining at {self.daily_task.start_dt - timedelta(minutes=5)}")

    def run_task_start_dialog(self):
        jobs_scheduler.add_job(
            func=start_user_dialog_job,
            trigger="date",
            next_run_time=self.daily_task.start_dt,
            replace_existing=True,
            kwargs={
                "user_id": self.user_id,
                "chat_id": self.chat_id,
                "task_data": self.daily_task.to_dict(exclude_none=True),
            }
        )
        logger.debug(f"scheduled begin dialog with {self.user_id} in chat {self.chat_id} about beginnin task {self.daily_task}")

    def run_task_end_dialog(self):
        jobs_scheduler.add_job(
            func=end_user_dialog_job,
            trigger="date",
            next_run_time=self.daily_task.end_dt,
            replace_existing=True,
            kwargs={
                "user_id": self.user_id,
                "chat_id": self.chat_id,
                "task_data": self.daily_task.to_dict(exclude_none=True),
            }
        )
