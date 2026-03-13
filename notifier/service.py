from datetime import timedelta, time

from loguru import logger

from daily_task.models import DailyTask
from db.session import get_db_session
from notifier.dao import UserNotifierSettingsDao
from notifier.models import UserNotifierSettings
from notifier.schemas import UpdatedSettings
from user.models import User

from notifier.base import jobs_scheduler
from notifier.jobs import send_user_msg_job, start_user_dialog_job, end_user_dialog_job


class UserNotifierSettingsService:
    @staticmethod
    async def get_user_settings(user_id: int) -> UserNotifierSettings | None:
        async with get_db_session(False) as session:
            return await UserNotifierSettingsDao(session).get_user_settings(user_id)

    @staticmethod
    async def update_user_settings(user_id: int, new_values: UpdatedSettings) -> UserNotifierSettings | None:
        async with get_db_session() as session:
            return await UserNotifierSettingsDao(session).update_user_settings(user_id, new_values.model_dump())


class NotifySchedulerService:
    def __init__(self, daily_task: DailyTask, user: User):
        self.daily_task = daily_task
        self.user = user

    async def add_notifier_jobs(self) -> None:
        user_settings = await UserNotifierSettingsService.get_user_settings(self.user.id)
        if not user_settings.enable_all_notifications:
            logger.warning(f"User {self.user.username} disabled all notifications")
        self.notify_before_task_start(user_settings)
        self.run_start_end_dialogs()

    def notify_before_task_start(self, notify_settings: UserNotifierSettings) -> None:
        for mins in notify_settings.mins_before_dt_start:
            notify_text = (f"hello {self.user.username}\n"
                           f"task {self.daily_task.name} will start starts in {mins} minutes")
            notify_time = self.daily_task.start_dt - timedelta(minutes=mins)
            jobs_scheduler.add_job(
                func=send_user_msg_job,
                trigger="date",
                next_run_time=notify_time,
                replace_existing=True,
                kwargs={"user_id": self.user.tg_id, "text": notify_text},
                id=f"{self.daily_task.id}:notify",
            )
            logger.debug(f"{self.user.username} should receive notification about task {self.daily_task.name} begining at {self.daily_task.start_dt - timedelta(minutes=5)}")

    def run_start_end_dialogs(self, notify_settings: UserNotifierSettings):
        if not notify_settings.progress_dt_notifications_enabled:
            logger.warning(f"user {self.user.username} disabled progress dialogs")
            return
        tasks_and_periods = [(start_user_dialog_job, self.daily_task.start_dt, "start_dialog"),
                             (end_user_dialog_job, self.daily_task.end_dt, "end_dialog")]
        for task, run_time, event_type in tasks_and_periods:
            jobs_scheduler.add_job(
                func=task,
                trigger="date",
                next_run_time=run_time,
                replace_existing=True,
                kwargs={
                    "user_id": self.user.tg_id,
                    "chat_id": self.user.tg_id,
                    "task_data": self.daily_task.to_dict(exclude_none=True),
                },
                id=f"{self.daily_task.id}:{event_type}",
            )

    @staticmethod
    def delete_dt_jobs(daily_task_id: int) -> None:
        for event_type in ["notify", "start_dialog", "end_dialog"]:
            job_id = f"{daily_task_id}:{event_type}"
            existing_job = jobs_scheduler.get_job(job_id)
            if existing_job:
                jobs_scheduler.remove_job(job_id)
                logger.debug(f"deleted job {job_id}")