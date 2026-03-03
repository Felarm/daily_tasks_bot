from aiogram_dialog import Dialog

from bot.daily_tasks_dialogs.handlers import DateTimeWidgetIds
from bot.daily_tasks_dialogs.states import DailyTaskCreationStates, DailyTaskCopyStates
from bot.daily_tasks_dialogs.windows import DailyTaskCreationWindows, CopyDailyTaskWindows, TaskBeginWindows

task_creation_dialog_router = Dialog(
    DailyTaskCreationWindows.get_name_input_window(),
    DailyTaskCreationWindows.get_description_input_window(),
    DailyTaskCreationWindows.get_date_input_window(
        header="input start date",
        calendar_id=DateTimeWidgetIds.start_dt.value,
        state=DailyTaskCreationStates.task_start_date,
    ),
    DailyTaskCreationWindows.get_time_input_window(
        header="input start time in HH:MM format",
        msg_input_id=DateTimeWidgetIds.start_dt.value,
        state=DailyTaskCreationStates.task_start_time,
    ),
    DailyTaskCreationWindows.get_date_input_window(
        header="input end date",
        calendar_id=DateTimeWidgetIds.end_dt.value,
        state=DailyTaskCreationStates.task_end_date,
    ),
    DailyTaskCreationWindows.get_time_input_window(
        header="input end time in HH:MM format",
        msg_input_id=DateTimeWidgetIds.end_dt.value,
        state=DailyTaskCreationStates.task_end_time,
    ),
    DailyTaskCreationWindows.get_confirmation_window(),
)


task_copy_dialog_router = Dialog(
    DailyTaskCreationWindows.get_date_input_window(
        header="select date you want copy to",
        calendar_id=DateTimeWidgetIds.start_dt.value,
        state=DailyTaskCopyStates.new_task_start_date,
    ),
    DailyTaskCreationWindows.get_time_input_window(
        header="input new start time in HH:MM format",
        msg_input_id=DateTimeWidgetIds.start_dt.value,
        state=DailyTaskCopyStates.new_task_start_time,
    ),
    CopyDailyTaskWindows.get_confirmation_window(),
)


task_begin_dialog_router = Dialog(
    TaskBeginWindows.get_task_begin_window(),
    TaskBeginWindows.get_task_end_window(),
)