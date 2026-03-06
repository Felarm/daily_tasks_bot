from db.session import get_db_session
from user.dao import UserDao
from user.models import User


class UserService:
    @staticmethod
    async def get_user_by_tg_id(tg_id: int) -> User | None:
        async with get_db_session(with_commit=False) as session:
            return await UserDao(session).get_by_tg_id(tg_id)

    @staticmethod
    async def register_new_user(
            username: str,
            tg_id: int | None = None,
            first_name: str | None = None,
            last_name: str | None = None,
    ) -> User | None:
        async with get_db_session() as session:
            await UserDao(session).new_user(username, tg_id, first_name, last_name)