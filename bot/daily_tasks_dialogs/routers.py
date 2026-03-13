from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode

from bot.daily_tasks_dialogs.keyboards import task_control_kb, TaskAction
from bot.daily_tasks_dialogs.states import DailyTaskCreationStates, DailyTaskCopyStates
from bot.users.keyboards import main_user_kb
from daily_task.service import DailyTaskService
from notifier.service import NotifySchedulerService

main_daily_tasks_router = Router()


@main_daily_tasks_router.callback_query(F.data == "get_today_tasks")
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


@main_daily_tasks_router.callback_query(F.data == "new_daily_task")
async def new_daily_task(callback: CallbackQuery, dialog_manager: DialogManager):
    await dialog_manager.start(state=DailyTaskCreationStates.name, mode=StartMode.RESET_STACK)


@main_daily_tasks_router.callback_query(TaskAction.filter(F.action == "delete"))
async def delete_task(callback: CallbackQuery, callback_data: TaskAction):
    task_id = callback_data.task_id
    await DailyTaskService.delete_task(task_id=task_id)
    await callback.message.answer(f"deleted task with {task_id=}", reply_markup=main_user_kb())
    NotifySchedulerService.delete_dt_jobs(task_id)


@main_daily_tasks_router.callback_query(TaskAction.filter(F.action == "copy"))
async def copy_task_to_date(callback: CallbackQuery, callback_data: TaskAction, dialog_manager: DialogManager):
    task = await DailyTaskService.get_task(callback_data.task_id)
    await dialog_manager.start(
        state=DailyTaskCopyStates.new_task_start_date,
        data={"task_to_copy": task.to_dict(exclude_none=True)},
        mode=StartMode.RESET_STACK,
    )