from typing import Callable, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import async_session_maker


class BaseDatabaseMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message | CallbackQuery, dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,
            data: dict[str, Any],
    ) -> Any:
        async with async_session_maker() as session:
            self.set_session(data, session)
            try:
                result = await handler(event, data)
                await self.after_handler(session)
                return result
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()

    def set_session(self, data: dict[str, Any], session: AsyncSession) -> None:
        raise NotImplementedError("method for adding db session to dialog is needed")

    async def after_handler(self, session: AsyncSession) -> None:
        pass


class DBMiddlewareWithoutCommit(BaseDatabaseMiddleware):
    def set_session(self, data: dict[str, Any], session: AsyncSession) -> None:
        data["session_without_commit"] = session


class DBMiddlewareWithCommit(BaseDatabaseMiddleware):
    def set_session(self, data: dict[str, Any], session: AsyncSession) -> None:
        data["session_with_commit"] = session

    async def after_handler(self, session: AsyncSession) -> None:
        await session.commit()

