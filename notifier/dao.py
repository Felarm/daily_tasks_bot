from datetime import time

from loguru import logger
from sqlalchemy import insert, select, update
from sqlalchemy.exc import SQLAlchemyError

from db.dao import BaseDao
from notifier.models import UserNotifierSettings


class UserNotifierSettingsDao(BaseDao[UserNotifierSettings]):
    model = UserNotifierSettings

    async def create_user_settings(self, user_id: int) -> UserNotifierSettings | None:
        query = insert(self.model).values(user_id=user_id).returning(self.model)
        try:
            result = await self._session.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error occurred during creation notify settings for user with {user_id=}\n{e}")
            raise

    async def get_user_settings(self, user_id: int) -> UserNotifierSettings | None:
        query = select(self.model).filter_by(user_id=user_id)
        try:
            result = await self._session.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error occurred while attempting to get user notify settings for user with {user_id=}\n{e}")
            raise

    async def update_user_settings(self, user_id: int, update_values: dict[str, bool | list | time]) -> None:
        query = update(self.model).where(self.model.user_id == user_id).values(**update_values)
        try:
            await self._session.execute(query)
        except SQLAlchemyError as e:
            logger.error(f"Error occurred while attempting to update user notify settigns for user with {user_id=} and {update_values=}\n{e}")
            raise
