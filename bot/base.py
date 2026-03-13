from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import ExceptionTypeFilter
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ErrorEvent
from aiogram_dialog import setup_dialogs, DialogManager
from aiogram_dialog.api.exceptions import UnknownIntent

from config import settings


bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
bg_factory = setup_dialogs(dp)


@dp.error()
async def simple_error_handler(event: ErrorEvent, dialog_manager: DialogManager) -> None:
    error_msg = f"something went wrong"
    if event.update.message:
        if event.update.message.from_user.id in settings.TG_ADMIN_IDS:
            await event.update.message.answer(str(event.exception))
        else:
            await event.update.message.answer(error_msg)
    elif event.update.callback_query:
        await event.update.callback_query.message.answer(error_msg)
    await dialog_manager.reset_stack()
