from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery
from typing import Callable, Any, Awaitable


class ClearInlineKeyboardMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[CallbackQuery, dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: dict[str, Any]
    ) -> Any:
        result = await handler(event, data)
        if event.message and event.message.reply_markup:
            await event.message.edit_reply_markup(reply_markup=None)
        return result
