from aiogram_dialog import StartMode

from bot.base import bot, bg_factory
from bot.daily_tasks_dialogs.states import DailyTaskProgressStates


async def send_user_msg_job(tg_user_id: int, text: str):
    await bot.send_message(chat_id=tg_user_id, text=text)


async def start_user_dialog_job(tg_user_id: int, chat_id: int, task_data: dict):
    dialog_mgr = bg_factory.bg(bot, tg_user_id, chat_id)
    await dialog_mgr.start(
        state=DailyTaskProgressStates.begin_state,
        mode=StartMode.RESET_STACK,
        data={"task_data": task_data},
    )


async def end_user_dialog_job(tg_user_id: int, chat_id: int, task_data: dict):
    dialog_mgr = bg_factory.bg(bot, tg_user_id, chat_id)
    await dialog_mgr.start(
        state=DailyTaskProgressStates.end_state,
        mode=StartMode.RESET_STACK,
        data={"task_data": task_data}
    )
