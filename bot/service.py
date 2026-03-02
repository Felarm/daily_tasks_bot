from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram_dialog import setup_dialogs
from loguru import logger

from bot.base import bot, dp
from bot.daily_tasks_dialogs.dialog import task_creation_dialog_router, task_copy_dialog_router
from bot.users.router import user_router
from config import settings
from bot.database_middleware import DBMiddlewareWithoutCommit, DBMiddlewareWithCommit


async def set_commands():
    commands = [
        BotCommand(command="start", description="start")
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def start_bot():
    setup_dialogs(dp)
    dp.update.middleware.register(DBMiddlewareWithoutCommit())
    dp.update.middleware.register(DBMiddlewareWithCommit())
    await set_commands()
    dp.include_router(user_router)
    dp.include_router(task_creation_dialog_router)
    dp.include_router(task_copy_dialog_router)
    await bot.set_webhook(
        url=settings.hook_url,
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True,
    )
    logger.debug(f"tg webhook is set to {settings.hook_url}")
    for tg_admin_id in settings.TG_ADMIN_IDS:
        try:
            await bot.send_message(tg_admin_id, "bot started bruh")
        except:
            pass
    logger.info("bot launched")


async def stop_bot():
    for tg_admin_id in settings.TG_ADMIN_IDS:
        try:
            await bot.send_message(tg_admin_id, "bot stopped bruh")
        except:
            pass
    logger.info("bot stopped")
