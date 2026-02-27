from datetime import datetime, timedelta

from loguru import logger

from config import jobs_scheduler
from scheduler.jobs import send_user_msg_job
from scheduler.schemas import UserNotifierDailyTaskDataSchema


class SchedulerService:
    @staticmethod
    def add_task_notify_job(daily_task_data: dict):
        """notifies user about task start in minutes... for now"""
        task_model = UserNotifierDailyTaskDataSchema(**daily_task_data)
        task_start_dtime = datetime.fromisoformat(task_model.start_dt)
        notifications = [
            {
                "time": task_start_dtime - timedelta(minutes=5),
                "text": f"bruh, task {task_model.name} starts in 5 minutes and should be ended by {task_model.end_dt}"
            }
        ]
        for notification in notifications:
            jobs_scheduler.add_job(
                send_user_msg_job,
                "date",
                next_run_time=notification["time"],
                kwargs={
                    "user_id": task_model.user_id,
                    "text": notification["text"],
                },
                replace_existing=True,
            )
            logger.debug(
                f"Scheduled notification for {task_model.user_id} on {notification["time"]} about task: {task_model.id}-{task_model.name}")