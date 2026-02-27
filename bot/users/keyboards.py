from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class TaskAction(CallbackData, prefix="task"):
    action: str
    task_id: int


def main_user_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="Schedule new daily task", callback_data="new_daily_task"))
    kb.add(InlineKeyboardButton(text="Get today tasks", callback_data="get_today_tasks"))
    kb.adjust(1)
    return kb.as_markup()


def task_control_kb(task_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Copy task", callback_data=TaskAction(action="copy_to_date", task_id=task_id))
    kb.button(text="Delete task", callback_data=TaskAction(action="delete", task_id=task_id))
    kb.adjust(1)
    return kb.as_markup()
