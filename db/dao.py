from datetime import date, datetime, time
from typing import Sequence, TypeVar, Generic, Type

from loguru import logger
from sqlalchemy import select, insert, delete, update
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import Base
from db.models import User, DailyTask, DTaskState
from db.schemas import NotifySettingsSchema

T = TypeVar("T", bound=Base)


class BaseDao(Generic[T]):
    model: Type[T] = None

    def __init__(self, session: AsyncSession):
        self._session = session
        if self.model is None:
            raise ValueError("No model passed")

    async def get_one_or_none_by_id(self, id_: int) -> T | None:
        try:
            result = await self._session.get_one(self.model, id_)
            return result
        except NoResultFound:
            logger.error(f"Not found record for {self.model.__name__} with id: {id_}")
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error occured when looking record for {self.model.__name__} with id {id_}:\n{e}")
            raise


class UserDao(BaseDao[User]):
    model = User

    async def new_user(
            self,
            username: str,
            id_: int,
            first_name: str | None = None,
            last_name: str | None = None,
            language_code: str | None = None,
    ) -> int | None:
        user_query = insert(self.model).values(
            username=username,
            id=id_,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
        ).returning(self.model.id)
        try:
            result = await self._session.execute(user_query)
            new_user_id = result.scalar_one_or_none()
            logger.info(f"registered user with id: {new_user_id}")
            return new_user_id
        except SQLAlchemyError as e:
            logger.error(f"Error occurred during registering new user with {username=}:\n{e}")

    async def get_by_username(self, username: str) -> User | None:
        query = select(self.model).filter_by(username=username)
        try:
            result = await self._session.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error occurred while attempting to get user by its {username=}:\n{e}")

    async def update_user_notify_settings(self, user_id: int, new_values: NotifySettingsSchema):
        user = await self.get_one_or_none_by_id(user_id)
        user.notify_settings = new_values.model_dump()
        try:
            await self._session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Error occurred while attempting to update notify_settings of user with {user_id=}\n{e}")


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
