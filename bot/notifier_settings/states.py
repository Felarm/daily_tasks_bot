from aiogram.fsm.state import StatesGroup, State


class CommonSettingsStates(StatesGroup):
    edit = State()
    view = State()


class SpecificSettingsStates(StatesGroup):
    mins_before_dt_start = State()
    today_dt_list_notification_time = State()
    today_dt_completion_analyze_time = State()
    task_progress_delay_mins = State()