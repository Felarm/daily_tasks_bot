from aiogram_dialog import Dialog

from bot.daily_tasks.task_progress.handlers import ApproveWidgetsIds
from bot.daily_tasks.task_progress.states import DailyTaskProgressStates
from bot.daily_tasks.task_progress.windows import TaskProgressWindows

task_progress_dialog_router = Dialog(
    TaskProgressWindows.get_task_progress_window(
        header="did u begin task?",
        approve_id=ApproveWidgetsIds.begin_approve,
        delay_id=ApproveWidgetsIds.delay_start,
        disapprove_id=ApproveWidgetsIds.begin_disapprove,
        state=DailyTaskProgressStates.begin_state,
    ),
    TaskProgressWindows.get_task_progress_window(
        header="did u end task?",
        approve_id=ApproveWidgetsIds.end_approve,
        delay_id=ApproveWidgetsIds.delay_end,
        disapprove_id=ApproveWidgetsIds.end_disapprove,
        state=DailyTaskProgressStates.end_state,
    ),
)
