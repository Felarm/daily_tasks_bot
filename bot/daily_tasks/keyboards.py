from dataclasses import dataclass

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


@dataclass
class KbDTPlanRoutes:
    new_daily_task = "new_daily_task"
    get_today_tasks = "get_today_tasks"
    get_active_tasks = "get_active_tasks"
    delete_task = "delete"
    copy_task_to_date = "copy"


@dataclass
class KbDTProgressRoutes:
    approve_task = "approve_task"
    disapprove_task = "disapprove_task"
    delay_task = "delay_task"


class DTPlanActions(CallbackData, prefix="task_planning"):
    action: str
    task_id: int


class DTProgressActions(CallbackData, prefix="task_progress"):
    action: str
    task_id: int
    event: str


def task_control_kb(task_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Copy task", callback_data=DTPlanActions(action=KbDTPlanRoutes.copy_task_to_date, task_id=task_id))
    kb.button(text="Delete task", callback_data=DTPlanActions(action=KbDTPlanRoutes.delete_task, task_id=task_id))
    kb.adjust(1)
    return kb.as_markup()


def task_progress_kb(task_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Begin", callback_data=DTProgressActions(action=KbDTProgressRoutes.approve_task, task_id=task_id, event=""))
    kb.button(text="End", callback_data=DTProgressActions(action=KbDTProgressRoutes.disapprove_task, task_id=task_id, event=""))
    kb.adjust(1)
    return kb.as_markup()


def task_notify_response_kb(task_id: int, event: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Yup", callback_data=DTProgressActions(action=KbDTProgressRoutes.approve_task, task_id=task_id, event=event))
    kb.button(text="Nope", callback_data=DTProgressActions(action=KbDTProgressRoutes.disapprove_task, task_id=task_id, event=event))
    kb.button(text="Delay", callback_data=DTProgressActions(action=KbDTProgressRoutes.delay_task, task_id=task_id, event=event))
    kb.adjust(1)
    return kb.as_markup()