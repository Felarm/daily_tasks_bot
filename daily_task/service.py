from datetime import datetime, date
from typing import Sequence

from daily_task.dao import DailyTaskDao
from daily_task.models import DailyTask, DTaskState
from db.session import get_db_session
from notifier.tg_notifier import TgDTaskNotifier
from user.service import UserService


class DailyTaskService:
    @staticmethod
    async def new_user_task(
            user_id: int,
            name: str,
            start_dt: datetime,
            end_dt: datetime,
            description: str | None = None
    ) -> DailyTask | None:
        async with get_db_session() as session:
            return await DailyTaskDao(session).create_user_daily_task(
                user_id, name, start_dt, end_dt, description
            )

    @staticmethod
    async def new_user_task_from_tg(
            tg_user_id: int,
            name: str,
            start_dt: datetime,
            end_dt: datetime,
            description: str | None = None
    ) -> DailyTask | None:
        user = await UserService.get_user_by_tg_id(tg_user_id)
        async with get_db_session() as session:
            new_task = await DailyTaskDao(session).create_user_daily_task(user.id, name, start_dt, end_dt, description)
            if not new_task:
                return None
            return new_task

    @staticmethod
    async def get_today_tasks_from_tg(tg_user_id: int) -> Sequence[DailyTask] | None:
        today = date.today()
        user = await UserService.get_user_by_tg_id(tg_user_id)
        async with get_db_session(with_commit=False) as session:
            return await DailyTaskDao(session).get_user_daily_tasks(user.id, today)

    @staticmethod
    async def get_active_tasks_from_tg(tg_user_id: int) -> Sequence[DailyTask] | None:
        user = await UserService.get_user_by_tg_id(tg_user_id)
        async with get_db_session(with_commit=False) as session:
            return await DailyTaskDao(session).get_daily_tasks_by_state(user.id, DTaskState.in_progress)

    @staticmethod
    async def delete_task(task_id: int) -> None:
        async with get_db_session() as session:
            await DailyTaskDao(session).delete_daily_task(task_id)

    @staticmethod
    async def get_task(task_id: int) -> DailyTask | None:
        async with get_db_session(with_commit=False) as session:
            return await DailyTaskDao(session).get_one_or_none_by_id(task_id)

    @staticmethod
    async def copy_task(task_id: int, new_start_dt: datetime) -> DailyTask | None:
        async with get_db_session(with_commit=True) as session:
            task_to_copy = await DailyTaskDao(session).get_one_or_none_by_id(task_id)
            if not task_to_copy:
                return None
            task_to_copy_duration = task_to_copy.end_dt - task_to_copy.start_dt
            new_end_dt = new_start_dt + task_to_copy_duration
            return await DailyTaskDao(session).create_user_daily_task(
                task_to_copy.user_id, task_to_copy.name, new_start_dt, new_end_dt, task_to_copy.description
            )

    @staticmethod
    async def begin_task(task_id: int, start_dt: datetime) -> None:
        """set task to in_progress state and adds real_start_dt"""
        async with get_db_session() as session:
            await DailyTaskDao(session).change_daily_task_state(task_id, DTaskState.in_progress)
            await DailyTaskDao(session).set_daily_task_real_start_dt(task_id, start_dt)

    @staticmethod
    async def fail_task(task_id: int) -> None:
        """set task to failed state"""
        async with get_db_session() as session:
            await DailyTaskDao(session).change_daily_task_state(task_id, DTaskState.failed)

    @staticmethod
    async def end_task(task_id: int, end_dt: datetime) -> None:
        """set task to done state and adds real_end_dt"""
        async with get_db_session() as session:
            await DailyTaskDao(session).change_daily_task_state(task_id, DTaskState.done)
            await DailyTaskDao(session).set_daily_task_real_end_dt(task_id, end_dt)