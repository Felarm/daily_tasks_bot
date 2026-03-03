from aiogram_dialog import Dialog

from bot.daily_tasks_dialogs.windows import NewDailyTaskCreationWindows, CopyDailyTaskWindows, TaskBeginWindows

task_creation_dialog_router = Dialog(
    NewDailyTaskCreationWindows.get_name_input_window(),
    NewDailyTaskCreationWindows.get_description_input_window(),
    NewDailyTaskCreationWindows.get_start_date_input_window(),
    NewDailyTaskCreationWindows.get_start_time_input_window(),
    NewDailyTaskCreationWindows.get_end_date_input_window(),
    NewDailyTaskCreationWindows.get_end_time_input_window(),
    NewDailyTaskCreationWindows.get_confirmation_window(),
)


task_copy_dialog_router = Dialog(
    CopyDailyTaskWindows.get_start_date_input_window(),
    CopyDailyTaskWindows.get_start_time_input_window(),
    CopyDailyTaskWindows.get_confirmation_window(),
)


task_begin_dialog_router = Dialog(
    TaskBeginWindows.get_task_begin_window(),
    TaskBeginWindows.get_task_end_window(),
)