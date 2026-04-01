import enum
from datetime import datetime, date, time, timedelta

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, ManagedCalendar

from bot.daily_tasks_dialogs.keyboards import task_control_kb
from bot.daily_tasks_dialogs.schemas import DTUnsavedSchema, DTProgressSchema, DTCopySchema
from bot.users.keyboards import main_user_kb
from daily_task.service import DailyTaskService
from notifier.tg_notifier import TgDTaskNotifier, DTaskNotifyEventTypes, TgUserNotifierSettings


class DateTimeWidgetIds(enum.Enum):
    start_dt = "start_dt"
    end_dt = "end_dt"


class ConfirmationWidgetIds(enum.Enum):
    create = "create"
    copy = "copy"
    delete = "delete"


class ApproveWidgetsIds(enum.Enum):
    begin_approve = "begin_approve"
    begin_disapprove = "begin_disapprove"
    delay_start = "delay_start"
    delay_end = "delay_end"
    end_approve = "end_approve"
    end_disapprove = "end_disapprove"


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
    if button.widget_id == ConfirmationWidgetIds.create.value:
        task_data = DTUnsavedSchema(tg_user_id=callback.from_user.id, **dialog_manager.dialog_data)
        created_task = await DailyTaskService.new_user_task_from_tg(**task_data.model_dump())
        await TgDTaskNotifier.add_created_task_notifications(callback.from_user.id, created_task)
        await callback.message.answer(
            text="new task created, now you can try to find it in your tasks list",
            reply_markup=main_user_kb(),
        )
    elif button.widget_id == ConfirmationWidgetIds.copy.value:
        task_data = DTCopySchema(**dialog_manager.start_data["task_to_copy"])
        new_start_dt: datetime = dialog_manager.dialog_data["start_dt"]
        await DailyTaskService.copy_task(task_data.id, new_start_dt)
        await callback.message.answer(
            text=f"task copied to {new_start_dt.isoformat(' ')}"
        )
    else:
        raise ValueError("unknow id of confirmation widget")

    await dialog_manager.done()


async def approve_progress(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    task_data = DTProgressSchema(**dialog_manager.start_data["task_data"])
    if button.widget_id == ApproveWidgetsIds.begin_approve.value:
        await DailyTaskService.begin_task(task_data.id, datetime.now())
        await callback.message.answer("ok, lets rooolll")
    elif button.widget_id == ApproveWidgetsIds.end_approve.value:
        await DailyTaskService.end_task(task_data.id, datetime.now())
        await callback.message.answer("yay, u did it")
    await dialog_manager.done()


async def delay_progress(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    user_settings = await TgUserNotifierSettings.get_tg_user_settings(callback.from_user.id)
    delay_mins = user_settings.task_progress_delay_mins
    task_data = DTProgressSchema(**dialog_manager.start_data["task_data"])
    notify_dt = datetime.now() + timedelta(minutes=delay_mins)
    if button.widget_id == ApproveWidgetsIds.delay_start.value:
        notify_event = DTaskNotifyEventTypes.start_dialog
        if notify_dt >= task_data.end_dt:
            await callback.message.answer(
                text="next_notification time is greater than planned task end\n"
                     "we'll mark this task as failed.\n"
                     "copy it to some other datetime or delete if you want",
                reply_markup=task_control_kb(task_data.id),
            )
            TgDTaskNotifier.delete_dt_jobs(task_data.id)
            await dialog_manager.done()
            return
    elif button.widget_id == ApproveWidgetsIds.delay_end.value:
        notify_event = DTaskNotifyEventTypes.end_dialog
        notify_dt = task_data.end_dt + timedelta(minutes=delay_mins)
        # todo some border point should be added to stop asking about delaying, may be next task start?
    else:
        await dialog_manager.done()
        return
    TgDTaskNotifier.reschedule_event(callback.from_user.id, task_data, notify_event, notify_dt)
    await callback.message.answer(f"ok, i'll comeback in {delay_mins} minutes")
    await dialog_manager.done()


async def disapprove_progress(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    task_data = DTProgressSchema(**dialog_manager.start_data["task_data"])
    await DailyTaskService.fail_task(task_data.id)
    TgDTaskNotifier.delete_dt_jobs(task_data.id)
    await callback.message.answer(
        text="we'll mark this task as failed.\nCopy it to some other datetime or delete if you want",
        reply_markup=task_control_kb(task_data.id),
    )
    await dialog_manager.done()
