from datetime import timedelta

from loguru import logger

from daily_task.models import DailyTask
from user.models import NotifySettingsSchema, User

from scheduler.base import jobs_scheduler
from scheduler.jobs import send_user_msg_job, start_user_dialog_job, end_user_dialog_job


class DTNotifySchedulerService:
    def __init__(self, daily_task: DailyTask, user: User):
        self.daily_task = daily_task
        self.user = user

    def add_tracker_jobs(self):
        self.notify_before_task_start()
        self.run_start_end_dialogs()

    def notify_before_task_start(self):
        user_settings = NotifySettingsSchema(**self.user.notify_settings)
        if not user_settings.enabled:
            logger.warning(f"user {self.user.username} disabled notifications")
        for mins in user_settings.mins_before_dt_start:
            notify_text = (f"hello {self.user.username}\n"
                           f"task {self.daily_task.name} will start starts in {mins} minutes")
            notify_time = self.daily_task.start_dt - timedelta(minutes=mins)
            jobs_scheduler.add_job(
                func=send_user_msg_job,
                trigger="date",
                next_run_time=notify_time,
                replace_existing=True,
                kwargs={"user_id": self.user.tg_id, "text": notify_text},
            )
            logger.debug(f"{self.user.username} should receive notification about task {self.daily_task.name} begining at {self.daily_task.start_dt - timedelta(minutes=5)}")

    def run_start_end_dialogs(self):
        tasks_and_periods = [(start_user_dialog_job, self.daily_task.start_dt),
                             (end_user_dialog_job, self.daily_task.end_dt)]
        for task, run_time in tasks_and_periods:
            jobs_scheduler.add_job(
                func=task,
                trigger="date",
                next_run_time=run_time,
                replace_existing=True,
                kwargs={
                    "user_id": self.user.tg_id,
                    "chat_id": self.user.tg_id,
                    "task_data": self.daily_task.to_dict(exclude_none=True),
                }
            )
