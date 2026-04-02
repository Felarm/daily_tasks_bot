from dataclasses import dataclass

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


@dataclass
class KbDTRoutes:
    new_daily_task = "new_daily_task"
    get_today_tasks = "get_today_tasks"
    get_active_tasks = "get_active_tasks"
    delete_task = "delete"
    copy_task_to_date = "copy"


class TaskAction(CallbackData, prefix="task"):
    action: str
    task_id: int


def task_control_kb(task_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Copy task", callback_data=TaskAction(action=KbDTRoutes.copy_task_to_date, task_id=task_id))
    kb.button(text="Delete task", callback_data=TaskAction(action=KbDTRoutes.delete_task, task_id=task_id))
    kb.adjust(1)
    return kb.as_markup()