from aiogram.types import BotCommand, BotCommandScopeDefault
from loguru import logger

from bot.base import bot, dp
from bot.daily_tasks.new_tasks_creation.dialogs import task_creation_dialog_router, task_copy_dialog_router
from bot.daily_tasks.routers import main_daily_tasks_router
from bot.daily_tasks.task_progress.dialogs import task_progress_dialog_router
from bot.notifier_settings.routers import notifier_settings_router
from bot.users.routers import user_router
from config import settings


async def start_bot():
    commands = [
        BotCommand(command="start", description="start")
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())
    dp.include_router(user_router)
    dp.include_router(notifier_settings_router)
    dp.include_router(main_daily_tasks_router)
    dp.include_router(task_creation_dialog_router)
    dp.include_router(task_copy_dialog_router)
    dp.include_router(task_progress_dialog_router)
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
