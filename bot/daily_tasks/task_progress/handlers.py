from dataclasses import dataclass
from datetime import datetime, timedelta

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from bot.daily_tasks.keyboards import task_control_kb
from bot.daily_tasks.schemas import DTProgressSchema
from daily_task.service import DailyTaskService
from notifier.tg_notifier import TgUserNotifierSettings, DTaskNotifyEventTypes, TgDTaskNotifier


@dataclass
class ApproveWidgetsIds:
    begin_approve = "begin_approve"
    begin_disapprove = "begin_disapprove"
    delay_start = "delay_start"
    delay_end = "delay_end"
    end_approve = "end_approve"
    end_disapprove = "end_disapprove"


async def approve_progress(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    task_data = DTProgressSchema(**dialog_manager.start_data["task_data"])
    if button.widget_id == ApproveWidgetsIds.begin_approve:
        await DailyTaskService.begin_task(task_data.id, datetime.now())
        await callback.message.answer("ok, lets rooolll")
    elif button.widget_id == ApproveWidgetsIds.end_approve:
        await DailyTaskService.end_task(task_data.id, datetime.now())
        await callback.message.answer("yay, u did it")
    await dialog_manager.done()


async def delay_progress(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    user_settings = await TgUserNotifierSettings.get_tg_user_settings(callback.from_user.id)
    delay_mins = user_settings.task_progress_delay_mins
    task_data = DTProgressSchema(**dialog_manager.start_data["task_data"])
    notify_dt = datetime.now() + timedelta(minutes=delay_mins)
    if button.widget_id == ApproveWidgetsIds.delay_start:
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
    elif button.widget_id == ApproveWidgetsIds.delay_end:
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
