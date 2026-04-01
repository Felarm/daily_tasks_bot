from datetime import time

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from loguru import logger

from bot.notifier_settings.keyboard import main_notify_settings_kb, edit_notify_settings_kb, EditSettingType, \
    SettingsNames, SettingsEditActions
from notifier.schemas import UpdatedSettings
from notifier.tg_notifier import TgUserNotifierSettings


class NotifySettingsStates(StatesGroup):
    mins_before_dt_start = State()
    today_dt_list_notification_time = State()
    today_dt_completion_analyze_time = State()
    task_progress_delay_mins = State()
    edit = State()
    view = State()


notifier_settings_router = Router()


@notifier_settings_router.callback_query(EditSettingType.filter(F.setting_action == SettingsEditActions.toggle))
async def update_setting_value_w_button(callback: CallbackQuery, callback_data: EditSettingType, state: FSMContext):
    await state.set_state(NotifySettingsStates.edit)
    curr_settings: UpdatedSettings = await state.get_value("user_settings")
    if callback_data.setting_name == SettingsNames.enable_all_notifications:
        curr_settings.enable_all_notifications = not curr_settings.enable_all_notifications
    elif callback_data.setting_name == SettingsNames.progress_dt_notifications_enabled:
        curr_settings.progress_dt_notifications_enabled = not curr_settings.progress_dt_notifications_enabled
    await state.update_data({"user_settings": curr_settings})
    await callback.message.answer(
        text="Setting updated, return to settings list or save changes", reply_markup=edit_notify_settings_kb(True)
    )


@notifier_settings_router.callback_query(EditSettingType.filter(F.setting_action == SettingsEditActions.message))
async def update_setting_value_w_message(callback: CallbackQuery, callback_data: EditSettingType, state: FSMContext):
    if callback_data.setting_name == SettingsNames.mins_before_dt_start:
        await state.set_state(NotifySettingsStates.mins_before_dt_start)
        await callback.message.answer(
            text="Input numbers, separated by commas (like '5, 10, 25' or '0, 1' or event '5')\n"
                 "These will be minutes that we will use for notifying you before task start",
            reply_markup=edit_notify_settings_kb(False)
        )
    elif callback_data.setting_name == SettingsNames.today_dt_list_notification_time:
        await state.set_state(NotifySettingsStates.today_dt_list_notification_time)
        await callback.message.answer(
            text="<b>Input time in HH:MM format</b>\n"
                 "Everyday at this time we will send you list of tasks planned for this day",
            reply_markup=edit_notify_settings_kb(False)
        )
    elif callback_data.setting_name == SettingsNames.today_dt_completion_analyze_time:
        await state.set_state(NotifySettingsStates.today_dt_completion_analyze_time)
        await callback.message.answer(
            text="<b>Input time in HH:MM format</b>\n"
                 "Everyday at this time we will send list of tasks that you completed/failed this day",
            reply_markup=edit_notify_settings_kb(False)
        )
    elif callback_data.setting_name == SettingsNames.task_progress_delay_mins:
        await state.set_state(NotifySettingsStates.task_progress_delay_mins)
        await callback.message.answer(
            text="Input number of minutes we will use for delaying task",
            reply_markup=edit_notify_settings_kb(False),
        )


def process_integer_num(input_value: str) -> int | None:
    try:
        return int(input_value)
    except ValueError:
        return None


@notifier_settings_router.message(NotifySettingsStates.task_progress_delay_mins)
async def edit_task_progress_delay_mins(message: Message, state: FSMContext):
    await state.set_state(NotifySettingsStates.edit)
    input_mins = process_integer_num(message.text)
    if not input_mins:
        await message.answer(text="Invalid input, try again", reply_markup=edit_notify_settings_kb(False))
        return
    curr_settings: UpdatedSettings = await state.get_value("user_settings")
    curr_settings.task_progress_delay_mins = input_mins
    await state.update_data({"user_settings": curr_settings})
    await message.answer(
        text="Setting updated, return to settings list or save changes",
        reply_markup=edit_notify_settings_kb(True),
    )


def process_string_of_nums(input_value: str) -> list[int] | None:
    try:
        return [int(_.strip()) for _ in input_value.split(",")]
    except ValueError:
        return None


@notifier_settings_router.message(NotifySettingsStates.mins_before_dt_start)
async def edit_mins_before_dt_start(message: Message, state: FSMContext):
    await state.set_state(NotifySettingsStates.edit)
    input_minutes = process_string_of_nums(message.text)
    if not input_minutes:
        await message.answer(text="Invalid input, try again", reply_markup=edit_notify_settings_kb(False))
        return
    curr_settings: UpdatedSettings = await state.get_value("user_settings")
    curr_settings.mins_before_dt_start = input_minutes
    await state.update_data({"user_settings": curr_settings})
    await message.answer(
        text="Setting updated, return to settings list or save changes",
        reply_markup=edit_notify_settings_kb(True),
    )


def process_time_from_string(input_value: str) -> time | None:
    try:
        return time.fromisoformat(input_value)
    except ValueError:
        return None


@notifier_settings_router.message(NotifySettingsStates.today_dt_list_notification_time)
async def edit_today_dt_list_notification_time(message: Message, state: FSMContext):
    await state.set_state(NotifySettingsStates.edit)
    input_time = process_time_from_string(message.text)
    if not input_time:
        await message.answer(
            text="HH:MM is something like 16:20 or 02:28, try again", reply_markup=edit_notify_settings_kb(False)
        )
        return
    curr_settings: UpdatedSettings = await state.get_value("user_settings")
    curr_settings.today_dt_list_notification_time = input_time
    await state.update_data({"user_settings": curr_settings})
    await message.answer(
        text="Setting updated, return to settings list or save changes", reply_markup=edit_notify_settings_kb(True)
    )


@notifier_settings_router.message(NotifySettingsStates.today_dt_completion_analyze_time)
async def edit_today_dt_completion_analyze_time(message: Message, state: FSMContext):
    await state.set_state(NotifySettingsStates.edit)
    input_time = process_time_from_string(message.text)
    if not input_time:
        await message.answer(
            text="HH:MM is something like 16:20 or 02:28, try again", reply_markup=edit_notify_settings_kb(False)
        )
        return
    curr_settings: UpdatedSettings = await state.get_value("user_settings")
    curr_settings.today_dt_completion_analyze_time = input_time
    await state.update_data({"user_settings": curr_settings})
    await message.answer(
        text="Setting updated, return to settings list or save changes", reply_markup=edit_notify_settings_kb(True)
    )


@notifier_settings_router.callback_query(F.data == "save_edit")
async def save_updated_settings(callback: CallbackQuery, state: FSMContext):
    current_settings: UpdatedSettings = await state.get_value("user_settings")
    await TgUserNotifierSettings.update_tg_user_settings(callback.from_user.id, current_settings)
    await state.set_state(NotifySettingsStates.view)
    await callback.message.answer("Settings saved", reply_markup=edit_notify_settings_kb(False))


@notifier_settings_router.callback_query(F.data == "get_user_settings")
async def get_user_settings(callback: CallbackQuery, state: FSMContext):
    curr_state = await state.get_state()
    if curr_state == NotifySettingsStates.edit:
        user_settings: UpdatedSettings = await state.get_value("user_settings")
        is_edit = True
    else:
        db_settings = await TgUserNotifierSettings.get_tg_user_settings(callback.from_user.id)
        user_settings = UpdatedSettings(**db_settings.to_dict())
        await state.set_data({"user_settings": user_settings})
        is_edit = False
    answer_txt = (f"Your current notification settings:\n"
                  f"- all notifications enabled: {user_settings.enable_all_notifications}\n"
                  f"- daily task prestart notifications: {user_settings.mins_before_dt_start}\n"
                  f"- daily task progress dialogs: {user_settings.progress_dt_notifications_enabled}\n"
                  f"- notification about all today tasks at: {user_settings.today_dt_list_notification_time}\n"
                  f"- todays tasks progress analyze dialog starts at: {user_settings.today_dt_completion_analyze_time}\n"
                  f"- task progress delay minutes: {user_settings.task_progress_delay_mins}\n\n"
                  f"You can change these settings using keyboard bellow")
    await callback.message.answer(answer_txt, reply_markup=main_notify_settings_kb(is_edit))
