from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.notifier_settings.keyboard import edit_notify_settings_kb
from bot.notifier_settings.states import CommonSettingsStates, SpecificSettingsStates
from notifier.schemas import UpdatedSettings


async def edit_enable_all_notifications(callback: CallbackQuery, state: FSMContext) -> None:
    settings: UpdatedSettings = await state.get_value("user_settings")
    await state.set_state(CommonSettingsStates.edit)
    settings.enable_all_notifications = not settings.enable_all_notifications


async def edit_progress_dt_notifications_enabled(callback: CallbackQuery, state: FSMContext) -> None:
    settings: UpdatedSettings = await state.get_value("user_settings")
    await state.set_state(CommonSettingsStates.edit)
    settings.progress_dt_notifications_enabled = not settings.progress_dt_notifications_enabled


async def edit_mins_before_dt_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(SpecificSettingsStates.mins_before_dt_start)
    await callback.message.answer(
        text="Input numbers, separated by commas (like '5, 10, 25' or '0, 1' or event '5')\n"
             "These will be minutes that we will use for notifying you before task start",
        reply_markup=edit_notify_settings_kb(False)
    )


async def edit_today_dt_list_notification_time(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(SpecificSettingsStates.today_dt_list_notification_time)
    await callback.message.answer(
        text="<b>Input time in HH:MM format</b>\n"
             "Everyday at this time we will send you list of tasks planned for this day",
        reply_markup=edit_notify_settings_kb(False)
    )


async def edit_today_dt_completion_analyze_time(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(SpecificSettingsStates.today_dt_completion_analyze_time)
    await callback.message.answer(
        text="<b>Input time in HH:MM format</b>\n"
             "Everyday at this time we will send list of tasks that you completed/failed this day",
        reply_markup=edit_notify_settings_kb(False)
    )


async def edit_task_progress_delay_mins(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(SpecificSettingsStates.task_progress_delay_mins)
    await callback.message.answer(
        text="Input number of minutes we will use for delaying task",
        reply_markup=edit_notify_settings_kb(False),
    )


settings_handlers = {
    "enable_all_notifications": edit_enable_all_notifications,
    "mins_before_dt_start": edit_mins_before_dt_start,
    "progress_dt_notifications_enabled": edit_progress_dt_notifications_enabled,
    "today_dt_list_notification_time": edit_today_dt_list_notification_time,
    "today_dt_completion_analyze_time": edit_today_dt_completion_analyze_time,
    "task_progress_delay_mins": edit_task_progress_delay_mins,
}