from loguru import logger
from sqlalchemy import insert, select
from sqlalchemy.exc import SQLAlchemyError

from db.dao import BaseDao
from user.models import User, NotifySettingsSchema


class UserDao(BaseDao[User]):
    model = User

    async def new_user(
            self,
            username: str,
            tg_id: int | None = None,
            first_name: str | None = None,
            last_name: str | None = None,
    ) -> User | None:
        user_query = insert(self.model).values(
            username=username,
            tg_id=tg_id,
            first_name=first_name,
            last_name=last_name,
        ).returning(self.model)
        try:
            result = await self._session.execute(user_query)
            new_user = result.scalar_one_or_none()
            logger.debug(f"registered user with id: {new_user.id}")
            return new_user
        except SQLAlchemyError as e:
            logger.error(f"Error occurred during registering new user with {username=}:\n{e}")

    async def get_by_username(self, username: str) -> User | None:
        query = select(self.model).filter_by(username=username)
        try:
            result = await self._session.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error occurred while attempting to get user by its {username=}:\n{e}")

    async def get_by_tg_id(self, tg_id: int) -> User | None:
        query = select(self.model).filter_by(tg_id=tg_id)
        try:
            result = await self._session.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error occurred whilt attempting to find user with {tg_id=}:\n{e}")

    async def update_user_notify_settings(self, user: User, new_values: NotifySettingsSchema):
        user.notify_settings = new_values.model_dump()
        try:
            await self._session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Error occurred while attempting to update notify_settings of user {user.username}\n{e}")

