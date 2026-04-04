from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram_dialog import setup_dialogs
from loguru import logger

from bot.base import bot, dp
from bot.daily_tasks.new_tasks_creation.dialogs import task_creation_dialog_router, task_copy_dialog_router
from bot.daily_tasks.routers.multiptle_tasks import get_multiple_tasks_router
from bot.daily_tasks.routers.single_task import plan_task_router, control_task_state_router
from bot.notifier_settings.routers import notifier_settings_router
from bot.users.routers import user_router
from config import settings


async def start_bot():
    commands = [
        BotCommand(command="start", description="start")
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())
    setup_dialogs(dp)
    dp.include_router(user_router)
    dp.include_router(notifier_settings_router)
    dp.include_router(get_multiple_tasks_router)
    dp.include_router(task_creation_dialog_router)
    dp.include_router(task_copy_dialog_router)
    dp.include_router(plan_task_router)
    dp.include_router(control_task_state_router)
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
