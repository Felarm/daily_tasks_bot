from aiogram_dialog import Dialog

from bot.daily_tasks_dialogs.getters import get_confirmed_new_task_info, get_confirmed_copy_task_info
from bot.daily_tasks_dialogs.handlers import DateTimeWidgetIds, ConfirmationWidgetIds, ApproveWidgetsIds
from bot.daily_tasks_dialogs.states import DailyTaskCreationStates, DailyTaskCopyStates, DailyTaskProgressStates
from bot.daily_tasks_dialogs.windows import DailyTaskCreationWindows, TaskProgressWindows


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
    DailyTaskCreationWindows.get_confirmation_window(
        action_id=ConfirmationWidgetIds.create.value,
        state=DailyTaskCreationStates.confirmation,
        getter=get_confirmed_new_task_info,
    ),
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
    DailyTaskCreationWindows.get_confirmation_window(
        action_id=ConfirmationWidgetIds.copy.value,
        state=DailyTaskCopyStates.confirmation,
        getter=get_confirmed_copy_task_info,
    ),
)


task_progress_dialog_router = Dialog(
    TaskProgressWindows.get_task_progress_window(
        header="did u begin task?",
        approve_id=ApproveWidgetsIds.begin_approve.value,
        delay_id=ApproveWidgetsIds.delay_start.value,
        disapprove_id=ApproveWidgetsIds.begin_disapprove.value,
        state=DailyTaskProgressStates.begin_state,
    ),
    TaskProgressWindows.get_task_progress_window(
        header="did u end task?",
        approve_id=ApproveWidgetsIds.end_approve.value,
        delay_id=ApproveWidgetsIds.delay_end.value,
        disapprove_id=ApproveWidgetsIds.end_disapprove.value,
        state=DailyTaskProgressStates.end_state,
    ),
)
