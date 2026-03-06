import enum
from datetime import datetime, date, time

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, ManagedCalendar
from sqlalchemy.ext.asyncio import AsyncSession

from bot.daily_tasks_dialogs.schemas import DTUnsavedSchema, DTBeginSchema
from bot.users.keyboards import main_user_kb, task_control_kb
from daily_task.dao import DailyTaskDao
from daily_task.models import DTaskState
from scheduler.service import DailyTaskSchedulerService


class DateTimeWidgetIds(enum.Enum):
    start_dt = "start_dt"
    end_dt = "end_dt"


class ConfirmationWidgetIds(enum.Enum):
    create = "create"
    copy = "copy"
    delete = "delete"


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


async def process_date_period(
        callback: CallbackQuery, widget: ManagedCalendar, dialog_mgr: DialogManager, selected_date: date
):
    calendar_id = widget.widget.widget_id
    if calendar_id == DateTimeWidgetIds.start_dt.value:
        dialog_mgr.dialog_data[calendar_id] = selected_date
        await dialog_mgr.next()
    if calendar_id == DateTimeWidgetIds.end_dt.value:
        if dialog_mgr.dialog_data.get(DateTimeWidgetIds.start_dt.value) is None:
            await callback.answer("there should be start datetime for setting end datetime")
            await dialog_mgr.back()
            return
        if selected_date < dialog_mgr.dialog_data[DateTimeWidgetIds.start_dt.value].date():
            await callback.answer("end of period should be greater than its start")
            await dialog_mgr.back()
            return
        dialog_mgr.dialog_data[calendar_id] = selected_date
        await dialog_mgr.next()


async def process_time_period(msg: Message, msg_input: MessageInput, dialog_mgr: DialogManager):
    try:
        input_time = time.fromisoformat(msg.text)
    except ValueError:
        await msg.answer("HH:MM is something like 16:20 or 02:28, try again")
        await dialog_mgr.back()
        return
    if msg_input.widget_id == DateTimeWidgetIds.start_dt.value:
        # start of period
        start_date: date = dialog_mgr.dialog_data[msg_input.widget_id]
        if datetime.combine(start_date, input_time) < datetime.now():
            await msg.answer("why do schedule anything in past?")
            await dialog_mgr.back()
            return
        dialog_mgr.dialog_data[msg_input.widget_id] = datetime.combine(start_date, input_time)
        await dialog_mgr.next()
        return
    if msg_input.widget_id == DateTimeWidgetIds.end_dt.value:
        # end of period
        end_date: date = dialog_mgr.dialog_data[msg_input.widget_id]
        if dialog_mgr.dialog_data.get(DateTimeWidgetIds.start_dt.value) is None:
            await msg.answer("there should be start datetime for setting end datetime")
            await dialog_mgr.back()
            return
        if datetime.combine(end_date, input_time) < dialog_mgr.dialog_data[DateTimeWidgetIds.start_dt.value]:
            await msg.answer("end of period should be greater than its start")
            await dialog_mgr.back()
            return
        dialog_mgr.dialog_data[msg_input.widget_id] = datetime.combine(end_date, input_time)
        await dialog_mgr.next()


async def create_confirmation(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, **_):
    session: AsyncSession = dialog_manager.middleware_data.get("session_with_commit")
    if button.widget_id == ConfirmationWidgetIds.create.value:
        task_data = DTUnsavedSchema(user_id=callback.from_user.id, **dialog_manager.dialog_data)
    elif button.widget_id == ConfirmationWidgetIds.copy.value:
        task_data = DTUnsavedSchema(**dialog_manager.start_data["task_to_copy"])
        task_to_copy_duration = task_data.end_dt - task_data.start_dt
        new_start_dt: datetime = dialog_manager.dialog_data["start_dt"]
        new_end_dt = new_start_dt + task_to_copy_duration
        task_data.start_dt = new_start_dt
        task_data.end_dt = new_end_dt
    else:
        raise ValueError("unknow id of confirmation widget")
    new_task = await DailyTaskDao(session).create_user_daily_task(**task_data.model_dump())
    await callback.message.answer(
        text="yay! we created another task, now you can try to find it in your tasks list",
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
