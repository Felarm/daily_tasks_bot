from datetime import date

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.daily_tasks_dialogs.states import DailyTaskCreationStates, DailyTaskCopyStates
from bot.users.keyboards import main_user_kb, task_control_kb, TaskAction
from bot.users.schemas import NewUserSchema
from db.dao import UserDao, DailyTaskDao

user_router = Router()


@user_router.message(CommandStart())
async def cmd_start(message: Message, session_with_commit: AsyncSession, state: FSMContext):
    await state.clear()
    existing_user = await UserDao(session_with_commit).get_one_or_none_by_id(message.from_user.id)
    if existing_user is None:
        new_user = NewUserSchema(
            id_=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            language_code=message.from_user.language_code,
        )
        await UserDao(session_with_commit).new_user(**new_user.model_dump())
    logger.debug("command start pressed")
    await message.answer("welcome!", reply_markup=main_user_kb())


@user_router.callback_query(F.data == "get_today_tasks")
async def get_today_tasks(callback: CallbackQuery, session_without_commit: AsyncSession):
    today = date.today()
    user_tasks = await DailyTaskDao(session_without_commit).get_user_daily_tasks(callback.from_user.id, today)
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


@user_router.callback_query(F.data == "new_daily_task")
async def new_daily_task(callback: CallbackQuery, dialog_manager: DialogManager):
    await callback.answer("yay, new task")
    await dialog_manager.start(state=DailyTaskCreationStates.name, mode=StartMode.RESET_STACK)


@user_router.callback_query(TaskAction.filter(F.action == "delete"))
async def delete_task(callback: CallbackQuery, callback_data: TaskAction, session_with_commit: AsyncSession):
    task_id = callback_data.task_id
    await DailyTaskDao(session_with_commit).delete_daily_task(task_id=task_id)
    await callback.answer(f"deleted task with {task_id=}")


@user_router.callback_query(TaskAction.filter(F.action == "copy_to_date"))
async def copy_task_to_date(callback: CallbackQuery, callback_data: TaskAction, session_without_commit: AsyncSession, dialog_manager: DialogManager):
    task = await DailyTaskDao(session_without_commit).get_one_or_none_by_id(callback_data.task_id)
    await dialog_manager.start(
        state=DailyTaskCopyStates.new_task_start_date,
        data={"task_to_copy": task.to_dict(exclude_none=True)},
        mode=StartMode.RESET_STACK,
    )