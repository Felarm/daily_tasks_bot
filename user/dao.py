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
            logger.debug(f"registered user with id: {new_user_id}")
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

