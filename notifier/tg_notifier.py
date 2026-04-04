from dataclasses import dataclass, asdict
from datetime import timedelta, time, datetime

from loguru import logger

from bot.daily_tasks.schemas import DTProgressSchema
from daily_task.models import DailyTask
from notifier.events import DTaskNotifyEventTypes
from notifier.models import UserNotifierSettings
from notifier.schemas import UpdatedSettings

from notifier.base import jobs_scheduler, UserNotifierSettingsService
from notifier.jobs import send_user_msg_job, ask_about_task_progress_job
from user.service import UserService


class TgUserNotifierSettings:
    @staticmethod
    async def get_tg_user_settings(tg_user_id: int) -> UserNotifierSettings | None:
        user = await UserService.get_user_by_tg_id(tg_user_id)
        return await UserNotifierSettingsService.get_user_settings(user.id)

    @staticmethod
    async def update_tg_user_settings(tg_user_id: int, new_values: UpdatedSettings) -> UserNotifierSettings | None:
        user = await UserService.get_user_by_tg_id(tg_user_id)
        return await UserNotifierSettingsService.update_user_settings(user.id, new_values)


EVENT_JOBS = {
    DTaskNotifyEventTypes.notify: send_user_msg_job,
    DTaskNotifyEventTypes.start_dialog: ask_about_task_progress_job,
    DTaskNotifyEventTypes.end_dialog: ask_about_task_progress_job,
}


class TgDTaskNotifier:
    @staticmethod
    async def add_created_task_notifications(tg_user_id: int, task: DailyTask) -> None:
        user_settings = await TgUserNotifierSettings.get_tg_user_settings(tg_user_id)
        if not user_settings.enable_all_notifications:
            logger.warning(f"user with id {user_settings.user_id} disabled all notifications")
        TgDTaskNotifier.notify_before_task_start(tg_user_id, task, user_settings)
        TgDTaskNotifier.run_task_progress_dialog(tg_user_id, task, user_settings)

    @staticmethod
    def notify_before_task_start(tg_user_id: int, task: DailyTask, notify_settings: UserNotifierSettings) -> None:
        for mins in notify_settings.mins_before_dt_start:
            notify_text = f"task {task.name} will start starts in {mins} minutes"
            notify_time = task.start_dt - timedelta(minutes=mins)
            jobs_scheduler.add_job(
                func=send_user_msg_job,
                trigger="date",
                next_run_time=notify_time,
                replace_existing=True,
                kwargs={"tg_user_id": tg_user_id, "text": notify_text},
                id=f"{task.id}:{DTaskNotifyEventTypes.notify}",
            )

    @staticmethod
    def run_task_progress_dialog(tg_user_id: int, task: DailyTask, notify_settings: UserNotifierSettings):
        if not notify_settings.progress_dt_notifications_enabled:
            logger.warning(f"user with id {notify_settings.user_id} disabled progress dialogs")
            return
        tasks_and_periods = [(ask_about_task_progress_job, task.start_dt, DTaskNotifyEventTypes.start_dialog),
                             (ask_about_task_progress_job, task.end_dt, DTaskNotifyEventTypes.end_dialog)]
        for job, run_time, event_type in tasks_and_periods:
            jobs_scheduler.add_job(
                func=job,
                trigger="date",
                next_run_time=run_time,
                replace_existing=True,
                kwargs={
                    "tg_user_id": tg_user_id,
                    "chat_id": tg_user_id,
                    "task_data": task.to_dict(exclude_none=True),
                    "event": event_type,
                },
                id=f"{task.id}:{event_type}",
            )

    @staticmethod
    def delete_dt_jobs(daily_task_id: int) -> None:
        for event_type in asdict(DTaskNotifyEventTypes()).values():
            job_id = f"{daily_task_id}:{event_type}"
            existing_job = jobs_scheduler.get_job(job_id)
            if existing_job:
                jobs_scheduler.remove_job(job_id)
                logger.debug(f"deleted notifier job {job_id}")

    @staticmethod
    def reschedule_event(tg_user_id: int, task_data: DTProgressSchema, event_type: str, new_dtime: datetime) -> None:
        event_job = EVENT_JOBS.get(event_type)
        if not event_job:
            return
        jobs_scheduler.add_job(
            func=event_job,
            trigger="date",
            next_run_time=new_dtime,
            replace_existing=True,
            kwargs={
                "tg_user_id": tg_user_id,
                "chat_id": tg_user_id,
                "task_data": task_data.model_dump(),
                "event": event_type,
            },
            id=f"{task_data.id}:{event_type}",
        )