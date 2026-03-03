from datetime import datetime, date, time

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from sqlalchemy.ext.asyncio import AsyncSession

from bot.daily_tasks_dialogs.schemas import NewDailyTaskSchema, DTUnsavedSchema, DTBeginSchema
from bot.users.keyboards import main_user_kb, task_control_kb
from db.dao import UserDao, DailyTaskDao
from db.models import DTaskState
from scheduler.service import DailyTaskSchedulerService


async def cancel_creation(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await callback.message.answer(
        text="ok, cancelled",
        reply_markup=main_user_kb(),
    )


async def process_name(msg: Message, msg_input: MessageInput, dialog_manager: DialogManager):
    task_name = msg.text
    dialog_manager.dialog_data["name"] = task_name
    await dialog_manager.next()


async def process_description(msg: Message, msg_input: MessageInput, dialog_manager: DialogManager):
    task_description = msg.text
    dialog_manager.dialog_data["description"] = task_description
    await dialog_manager.next()


async def process_start_date(callback: CallbackQuery, widget, dialog_manager: DialogManager, selected_date: date):
    dialog_manager.dialog_data["start_dt"] = selected_date
    await callback.answer("such a good start, lets plan start time")
    await dialog_manager.next()


async def process_start_time(msg: Message, msg_input: MessageInput, dialog_manager: DialogManager):
    try:
        input_time = time.fromisoformat(msg.text)
    except ValueError:
        await msg.answer("HH:MM is something like 16:20 or 02:28, try again")
        await dialog_manager.back()
        return
    if datetime.combine(dialog_manager.dialog_data["start_dt"], input_time) < datetime.now():
        await msg.answer("why do schedule anything in past?")
        await dialog_manager.back()
    else:
        dialog_manager.dialog_data["start_dt"] = datetime.combine(dialog_manager.dialog_data["start_dt"], input_time)
        await msg.answer("such a good start, lets plan end date")
        await dialog_manager.next()


async def process_end_date(callback: CallbackQuery, widget, dialog_manager: DialogManager, selected_date: date):
    if selected_date < dialog_manager.dialog_data["start_dt"].date():
        await callback.answer("bruh, task end date should be greater than its start")
        await dialog_manager.back()
    else:
        dialog_manager.dialog_data["end_dt"] = selected_date
        await callback.answer("great, we're almost done")
        await dialog_manager.next()


async def process_end_time(msg: Message, msg_input: MessageInput, dialog_manager: DialogManager):
    try:
        input_time = time.fromisoformat(msg.text)
    except ValueError:
        await msg.answer("HH:MM is something like 16:20 or 10:22, try again")
        await dialog_manager.back()
        return
    if datetime.combine(dialog_manager.dialog_data["end_dt"], input_time) < dialog_manager.dialog_data["start_dt"]:
        await msg.answer("bruh, task end should be greater than its start")
        await dialog_manager.back()
    else:
        dialog_manager.dialog_data["end_dt"] = datetime.combine(dialog_manager.dialog_data["end_dt"], input_time)
        await msg.answer("great, we're almost done")
        await dialog_manager.next()


async def create_confirmation(callback: CallbackQuery, widget, dialog_manager: DialogManager, **_):
    session: AsyncSession = dialog_manager.middleware_data.get("session_with_commit")
    user = await UserDao(session).get_one_or_none_by_id(callback.from_user.id)
    if not user:
        await callback.answer(f"how you did this? {callback.from_user.username} cant create tasks in our system")
        await dialog_manager.done()
    else:
        add_task = NewDailyTaskSchema(user_id=user.id, **dialog_manager.dialog_data)
        created_task = await DailyTaskDao(session).create_user_daily_task(**add_task.model_dump())
        await callback.message.answer(
            text="yay! we created new task, now you can try to find it in your tasks list",
            reply_markup=main_user_kb(),
        )
        await DailyTaskSchedulerService(
            created_task,
            callback.from_user.id,
            callback.message.chat.id
        ).add_tracker_jobs()
        await dialog_manager.done()


async def copy_confirmation(callback: CallbackQuery, widget, dialog_manager: DialogManager):
    session: AsyncSession = dialog_manager.middleware_data.get("session_with_commit")
    task_to_copy_data = DTUnsavedSchema(**dialog_manager.start_data["task_to_copy"])
    new_start_dt: datetime = dialog_manager.dialog_data["start_dt"]
    task_to_copy_duration = task_to_copy_data.end_dt - task_to_copy_data.start_dt
    new_end_dt = new_start_dt + task_to_copy_duration
    new_task = await DailyTaskDao(session).create_user_daily_task(
        user_id=callback.from_user.id,
        name=task_to_copy_data.name,
        start_dt=new_start_dt,
        end_dt=new_end_dt,
        description=task_to_copy_data.description,
    )
    await callback.message.answer(
        text=f"task copied to date {new_start_dt.isoformat(' ')}",
        reply_markup=main_user_kb(),
    )
    await DailyTaskSchedulerService(
        new_task,
        callback.from_user.id,
        callback.message.chat.id,
    ).add_tracker_jobs()
    await dialog_manager.done()


async def begin_approval(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session = dialog_manager.middleware_data.get("session_with_commit")
    task_data = DTBeginSchema(**dialog_manager.start_data["task_data"])
    now = datetime.now()
    if now > task_data.end_dt:
        # task is failed cause missed time to check in
        await DailyTaskDao(session).change_daily_task_state(task_data.id, DTaskState.failed)
        await callback.message.answer(
            text="bruh, task already ended, its fail to begin it. Copy it to some other datetime to begin again or just delete",
            reply_markup=task_control_kb(task_data.id),
        )
    else:
        await DailyTaskDao(session).change_daily_task_state(task_data.id, DTaskState.in_progres)
        await DailyTaskDao(session).set_daily_task_real_start_dt(task_data.id, now)
        await callback.message.answer("ok, lets rooolll")
    await dialog_manager.done()


async def begin_disapproval(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session = dialog_manager.middleware_data.get("session_with_commit")
    task_data = DTBeginSchema(**dialog_manager.start_data["task_data"])
    await DailyTaskDao(session).change_daily_task_state(task_data.id, DTaskState.failed)
    await callback.message.answer(
        text="we'll mark this task as failed. Copy it to some other datetime or delete if you want",
        reply_markup=task_control_kb(task_data.id),
    )
    await dialog_manager.done()


async def end_approval(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session = dialog_manager.middleware_data.get("session_with_commit")
    task_data = DTBeginSchema(**dialog_manager.start_data["task_data"])
    await DailyTaskDao(session).change_daily_task_state(task_data.id, DTaskState.done)
    await DailyTaskDao(session).set_daily_task_real_end_dt(task_data.id, datetime.now())
    await callback.message.answer("yay! u did it!")
    await dialog_manager.done()


async def end_disapproval(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session = dialog_manager.middleware_data.get("session_with_commit")
    task_data = DTBeginSchema(**dialog_manager.start_data["task_data"])
    await DailyTaskDao(session).change_daily_task_state(task_data.id, DTaskState.failed)
    await callback.message.answer(
        text="bruh, its failed, may be copy to other time?",
        reply_markup=task_control_kb(task_data.id),
    )
    await dialog_manager.done()
