from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_user_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="Schedule new daily task", callback_data="new_daily_task"))
    kb.add(InlineKeyboardButton(text="Get today tasks", callback_data="get_today_tasks"))
    kb.add(InlineKeyboardButton(text="Settings", callback_data="get_user_settings"))
    kb.adjust(1)
    return kb.as_markup()
