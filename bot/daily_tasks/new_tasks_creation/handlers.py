from dataclasses import dataclass
from datetime import date, time, datetime

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, ManagedCalendar

from bot.daily_tasks.schemas import DTUnsavedSchema, DTCopySchema
from bot.users.keyboards import main_user_kb
from daily_task.service import DailyTaskService
from notifier.tg_notifier import TgDTaskNotifier


@dataclass
class DateTimeWidgetIds:
    start_dt = "start_dt"
    end_dt = "end_dt"

@dataclass
class ConfirmationWidgetIds:
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
    if calendar_id == DateTimeWidgetIds.start_dt:
        dialog_mgr.dialog_data[calendar_id] = selected_date
        await dialog_mgr.next()
    if calendar_id == DateTimeWidgetIds.end_dt:
        if dialog_mgr.dialog_data.get(DateTimeWidgetIds.start_dt) is None:
            await callback.answer("there should be start datetime for setting end datetime")
            await dialog_mgr.back()
            return
        if selected_date < dialog_mgr.dialog_data[DateTimeWidgetIds.start_dt].date():
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
    if msg_input.widget_id == DateTimeWidgetIds.start_dt:
        # start of period
        start_date: date = dialog_mgr.dialog_data[msg_input.widget_id]
        if datetime.combine(start_date, input_time) < datetime.now():
            await msg.answer("why do schedule anything in past?")
            await dialog_mgr.back()
            return
        dialog_mgr.dialog_data[msg_input.widget_id] = datetime.combine(start_date, input_time)
        await dialog_mgr.next()
        return
    if msg_input.widget_id == DateTimeWidgetIds.end_dt:
        # end of period
        end_date: date = dialog_mgr.dialog_data[msg_input.widget_id]
        if dialog_mgr.dialog_data.get(DateTimeWidgetIds.start_dt) is None:
            await msg.answer("there should be start datetime for setting end datetime")
            await dialog_mgr.back()
            return
        if datetime.combine(end_date, input_time) < dialog_mgr.dialog_data[DateTimeWidgetIds.start_dt]:
            await msg.answer("end of period should be greater than its start")
            await dialog_mgr.back()
            return
        dialog_mgr.dialog_data[msg_input.widget_id] = datetime.combine(end_date, input_time)
        await dialog_mgr.next()


async def create_confirmation(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, **_):
    if button.widget_id == ConfirmationWidgetIds.create:
        task_data = DTUnsavedSchema(tg_user_id=callback.from_user.id, **dialog_manager.dialog_data)
        if task_data.start_dt <= datetime.now():
            await callback.message.answer("Task begin datetime is less then now, go back and edit input data")
            await dialog_manager.back()
            return
        created_task = await DailyTaskService.new_user_task_from_tg(**task_data.model_dump())
        await TgDTaskNotifier.add_created_task_notifications(callback.from_user.id, created_task)
        await callback.message.answer(
            text="new task created, now you can try to find it in your tasks list",
            reply_markup=main_user_kb(),
        )
    elif button.widget_id == ConfirmationWidgetIds.copy:
        task_data = DTCopySchema(**dialog_manager.start_data["task_to_copy"])
        new_start_dt: datetime = dialog_manager.dialog_data["start_dt"]
        if new_start_dt <= datetime.now():
            await callback.message.answer("Task begin datetime is less then now, go back and edit input data")
            await dialog_manager.back()
            return
        await DailyTaskService.copy_task(task_data.id, new_start_dt)
        await callback.message.answer(
            text=f"task copied to {new_start_dt.isoformat(' ')}"
        )
    else:
        raise ValueError("unknow id of confirmation widget")

    await dialog_manager.done()
