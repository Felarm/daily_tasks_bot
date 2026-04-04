from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.daily_tasks.keyboards import task_control_kb, KbDTPlanRoutes
from daily_task.service import DailyTaskService


get_multiple_tasks_router = Router()


@get_multiple_tasks_router.callback_query(F.data == KbDTPlanRoutes.get_active_tasks)
async def get_active_tasks(callback: CallbackQuery):
    active_tasks = await DailyTaskService.get_active_tasks_from_tg(callback.from_user.id)
    if not active_tasks:
        await callback.message.answer("no active tasks for now")
        return
    await callback.answer("here are your active tasks")
    for task in active_tasks:
        msg_text = (f"<b>{task.name}</b>\n"
                    f"{task.description}\n"
                    f"<b>start time:</b> {task.start_dt.time().isoformat()}\n"
                    f"<b>end time:</b> {task.end_dt.time().isoformat()}\n"
                    f"<b>state:</b> {task.state.value}")
        await callback.message.answer(msg_text, reply_markup=task_control_kb(task.id))


@get_multiple_tasks_router.callback_query(F.data == KbDTPlanRoutes.get_today_tasks)
async def get_today_tasks(callback: CallbackQuery):
    user_tasks = await DailyTaskService.get_today_tasks_from_tg(callback.from_user.id)
    if not user_tasks:
        await callback.message.answer("hmm.. no tasks for today")
        return
    await callback.answer("here are your today tasks")
    for task in user_tasks:
        msg_text = (f"<b>{task.name}</b>\n"
                    f"{task.description}\n"
                    f"<b>start time:</b> {task.start_dt.time().isoformat()}\n"
                    f"<b>end time:</b> {task.end_dt.time().isoformat()}\n"
                    f"<b>state:</b> {task.state.value}")
        await callback.message.answer(msg_text, reply_markup=task_control_kb(task.id))