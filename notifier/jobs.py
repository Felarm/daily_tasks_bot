from bot.base import bot, dp
from bot.daily_tasks.keyboards import task_notify_response_kb
from bot.daily_tasks.schemas import DTProgressSchema
from notifier.events import DTaskNotifyEventTypes


async def send_user_msg_job(tg_user_id: int, text: str):
    await bot.send_message(chat_id=tg_user_id, text=text)


async def ask_about_task_progress_job(tg_user_id: int, chat_id: int, task_data: dict, event: str):
    context = dp.fsm.resolve_context(bot=bot, chat_id=chat_id, user_id=tg_user_id)
    task = DTProgressSchema(**task_data)
    if event == DTaskNotifyEventTypes.start_dialog:
        text = f"Did you begin task '{task.name}'?"
    elif event == DTaskNotifyEventTypes.end_dialog:
        text = f"Did you end task '{task.name}'?"
    else:
        return
    await context.update_data({str(task.id): task_data})
    await bot.send_message(
        chat_id=tg_user_id, text=text, reply_markup=task_notify_response_kb(task.id, event)
    )
