from dataclasses import dataclass

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


@dataclass
class SettingsNames:
    enable_all_notifications = "enable_all_notifications"
    mins_before_dt_start = "mins_before_dt_start"
    progress_dt_notifications_enabled = "progress_dt_notifications_enabled"
    today_dt_list_notification_time = "today_dt_list_notification_time"
    today_dt_completion_analyze_time = "today_dt_completion_analyze_time"
    task_progress_delay_mins = "task_progress_delay_mins"


class EditSettingType(CallbackData, prefix="notify_settings"):
    setting_name: str


def main_notify_settings_kb(is_edited: bool) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text="Toggle all notifications",
        callback_data=EditSettingType(setting_name=SettingsNames.enable_all_notifications)
    )
    kb.button(
        text="Add prestart notification period",
        callback_data=EditSettingType(setting_name=SettingsNames.mins_before_dt_start)
    )
    kb.button(
        text="Toggle progress dialogs",
        callback_data=EditSettingType(setting_name=SettingsNames.progress_dt_notifications_enabled)
    )
    kb.button(
        text="Set time of notification about today tasks",
        callback_data=EditSettingType(setting_name=SettingsNames.today_dt_list_notification_time)
    )
    kb.button(
        text="Set time for analyze dialog for todays tasks",
        callback_data=EditSettingType(setting_name=SettingsNames.today_dt_completion_analyze_time)
    )
    kb.button(
        text="Set amount of minutes for delaying task",
        callback_data=EditSettingType(setting_name=SettingsNames.task_progress_delay_mins)
    )
    if is_edited:
        kb.button(text="Save", callback_data="save_edit")
    kb.adjust(1)
    return kb.as_markup()


def edit_notify_settings_kb(w_save: bool) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Back to settings list", callback_data="get_user_settings")
    if w_save:
        kb.button(text="Save", callback_data="save_edit")
    kb.adjust(1)
    return kb.as_markup()

