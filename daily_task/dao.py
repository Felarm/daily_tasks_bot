from datetime import datetime, date, time
from typing import Sequence

from loguru import logger
from sqlalchemy import insert, select, delete, update
from sqlalchemy.exc import SQLAlchemyError

from daily_task.models import DailyTask, DTaskState
from db.dao import BaseDao


class DailyTaskDao(BaseDao[DailyTask]):
    model = DailyTask

    async def create_user_daily_task(
            self,
            user_id: int,
            name: str,
            start_dt: datetime,
            end_dt: datetime,
            description: str | None = None,
    ) -> DailyTask | None:
        query = insert(self.model).values(
            user_id=user_id,
            name=name,
            start_dt=start_dt,
            end_dt=end_dt,
            description=description,
        ).returning(self.model)
        try:
            result = await self._session.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error occurred while creating task for user {user_id=}:\n{e}")

    async def get_user_daily_tasks(self, user_id: int, tasks_date: date | None = None) -> Sequence[DailyTask] | None:
        query = select(self.model).filter_by(user_id=user_id)
        if tasks_date:
            query = query.where(
                datetime.combine(tasks_date, time.min) <= self.model.start_dt
            ).where(
                self.model.start_dt <= datetime.combine(tasks_date, time.max)
            )
        try:
            result = await self._session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error occurred while getting user tasks for {user_id=}:\n{e}")

    async def delete_daily_task(self, task_id: int) -> None:
        query = delete(self.model).where(self.model.id == task_id)
        try:
            await self._session.execute(query)
        except SQLAlchemyError as e:
            logger.error(f"Error occurred while deleting task with {task_id=}:\n{e}")

    async def change_daily_task_state(self, task_id: int, new_state: DTaskState) -> None:
        query = update(self.model).where(self.model.id == task_id).values(state=new_state.value)
        try:
            await self._session.execute(query)
        except SQLAlchemyError as e:
            logger.error(f"Error occurred while changing task with {task_id=} state to {new_state.value}:\n{e}")

    async def set_daily_task_real_start_dt(self, task_id: int, real_start_dt: datetime):
        query = update(self.model).where(self.model.id == task_id).values(real_start_dt=real_start_dt)
        try:
            await self._session.execute(query)
        except SQLAlchemyError as e:
            logger.error(f"Error occurred while setting real_start_dt of task with {task_id=} to {real_start_dt}:\n{e}")

    async def set_daily_task_real_end_dt(self, task_id: int, real_end_dt: datetime):
        query = update(self.model).where(self.model.id == task_id).values(real_end_dt=real_end_dt)
        try:
            await self._session.execute(query)
        except SQLAlchemyError as e:
            logger.error(f"Error occurred while setting real_end_dt of task with {task_id=} to {real_end_dt}:\n{e}")
