from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class TaskAction(CallbackData, prefix="task"):
    action: str
    task_id: int


def task_control_kb(task_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Copy task", callback_data=TaskAction(action="copy", task_id=task_id))
    kb.button(text="Delete task", callback_data=TaskAction(action="delete", task_id=task_id))
    kb.adjust(1)
    return kb.as_markup()