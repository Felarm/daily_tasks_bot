from datetime import datetime, timedelta

from loguru import logger

from config import jobs_scheduler
from db.dao import UserDao
from db.session import get_db_session
from scheduler.jobs import send_user_msg_job
from scheduler.schemas import UserNotifierDailyTaskDataSchema


class SchedulerService:
    @staticmethod
    async def add_task_notify_job(daily_task_data: dict):
        """notifies user about task start in minutes... for now"""
        task_model = UserNotifierDailyTaskDataSchema(**daily_task_data)
        task_start_dtime = datetime.fromisoformat(task_model.start_dt)
        async with get_db_session(False) as db_session:
            task_user = await UserDao(db_session).get_one_or_none_by_id(task_model.user_id)
        if not task_user.notify_settings["enabled"]:
            logger.warning(f"notifications are disabled for {task_user.username}")
            return
        notifications = []
        for mins in task_user.notify_settings["mins_before_dt_start"]:
            notifications.append(
                {
                    "time": task_start_dtime - timedelta(minutes=mins),
                    "text": f"hey {task_user.username}, task {task_model.name} starts in {mins} minutes and should be ended by {task_model.end_dt}"
                }
            )
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
                f"Scheduled notification for {task_user.username} on {notification["time"]} about task: {task_model.id}-{task_model.name}")
