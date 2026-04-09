from dataclasses import dataclass

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from daily_task.models import DTaskState
from notifier.events import DTaskNotifyEventTypes


@dataclass
class KbDTPlanRoutes:
    new_daily_task = "new_daily_task"
    get_today_tasks = "get_today_tasks"
    get_active_tasks = "get_active_tasks"
    get_current_hour_tasks = "get_current_hour_tasks"
    delete_task = "delete"
    copy_task_to_date = "copy"


@dataclass
class KbDTProgressRoutes:
    approve_task = "approve_task"
    disapprove_task = "disapprove_task"
    delay_task = "delay_task"
    begin_task = "begin_task"
    end_task = "end_task"


class DTPlanActions(CallbackData, prefix="task_planning"):
    route: str
    task_id: int


class DTProgressActions(CallbackData, prefix="task_progress"):
    route: str
    task_id: int
    event: str


def task_control_kb(task_id: int, task_state: DTaskState = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if task_state in [DTaskState.created, DTaskState.in_progress]:
        if task_state == DTaskState.created:
            text = "Begin task"
            route = KbDTProgressRoutes.begin_task
            event = DTaskNotifyEventTypes.begin_task
        else:
            text = "End task"
            route = KbDTProgressRoutes.end_task
            event = DTaskNotifyEventTypes.end_task
        kb.button(text=text, callback_data=DTProgressActions(route=route, task_id=task_id, event=event))
    kb.button(text="Copy task", callback_data=DTPlanActions(route=KbDTPlanRoutes.copy_task_to_date, task_id=task_id))
    kb.button(text="Delete task", callback_data=DTPlanActions(route=KbDTPlanRoutes.delete_task, task_id=task_id))
    kb.adjust(1)
    return kb.as_markup()


def task_notify_response_kb(task_id: int, event: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Yup", callback_data=DTProgressActions(route=KbDTProgressRoutes.approve_task, task_id=task_id, event=event))
    kb.button(text="Nope", callback_data=DTProgressActions(route=KbDTProgressRoutes.disapprove_task, task_id=task_id, event=event))
    kb.button(text="Delay", callback_data=DTProgressActions(route=KbDTProgressRoutes.delay_task, task_id=task_id, event=event))
    kb.adjust(1)
    return kb.as_markup()