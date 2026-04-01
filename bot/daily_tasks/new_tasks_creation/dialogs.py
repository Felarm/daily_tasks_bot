from aiogram_dialog import Dialog

from bot.daily_tasks.new_tasks_creation.getters import get_confirmed_new_task_info, get_confirmed_copy_task_info
from bot.daily_tasks.new_tasks_creation.handlers import DateTimeWidgetIds, ConfirmationWidgetIds
from bot.daily_tasks.new_tasks_creation.states import DailyTaskCreationStates, DailyTaskCopyStates
from bot.daily_tasks.new_tasks_creation.windows import DailyTaskCreationWindows


task_creation_dialog_router = Dialog(
    DailyTaskCreationWindows.get_name_input_window(),
    DailyTaskCreationWindows.get_description_input_window(),
    DailyTaskCreationWindows.get_date_input_window(
        header="input start date",
        calendar_id=DateTimeWidgetIds.start_dt,
        state=DailyTaskCreationStates.task_start_date,
    ),
    DailyTaskCreationWindows.get_time_input_window(
        header="input start time in HH:MM format",
        msg_input_id=DateTimeWidgetIds.start_dt,
        state=DailyTaskCreationStates.task_start_time,
    ),
    DailyTaskCreationWindows.get_date_input_window(
        header="input end date",
        calendar_id=DateTimeWidgetIds.end_dt,
        state=DailyTaskCreationStates.task_end_date,
    ),
    DailyTaskCreationWindows.get_time_input_window(
        header="input end time in HH:MM format",
        msg_input_id=DateTimeWidgetIds.end_dt,
        state=DailyTaskCreationStates.task_end_time,
    ),
    DailyTaskCreationWindows.get_confirmation_window(
        action_id=ConfirmationWidgetIds.create,
        state=DailyTaskCreationStates.confirmation,
        getter=get_confirmed_new_task_info,
    ),
)


task_copy_dialog_router = Dialog(
    DailyTaskCreationWindows.get_date_input_window(
        header="select date you want copy to",
        calendar_id=DateTimeWidgetIds.start_dt,
        state=DailyTaskCopyStates.new_task_start_date,
    ),
    DailyTaskCreationWindows.get_time_input_window(
        header="input new start time in HH:MM format",
        msg_input_id=DateTimeWidgetIds.start_dt,
        state=DailyTaskCopyStates.new_task_start_time,
    ),
    DailyTaskCreationWindows.get_confirmation_window(
        action_id=ConfirmationWidgetIds.copy,
        state=DailyTaskCopyStates.confirmation,
        getter=get_confirmed_copy_task_info,
    ),
)
