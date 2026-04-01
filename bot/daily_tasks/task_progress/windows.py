from aiogram.fsm.state import State
from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

from bot.daily_tasks.task_progress.handlers import approve_progress, delay_progress, disapprove_progress


class TaskProgressWindows:
    @staticmethod
    def get_task_progress_window(
            header: str, approve_id: str, delay_id: str, disapprove_id: str, state: State
    ) -> Window:
        return Window(
            Const(header),
            Button(Const("yup"), id=approve_id, on_click=approve_progress),
            Button(Const("not yet"), id=delay_id, on_click=delay_progress),
            Button(Const("nope"), id=disapprove_id, on_click=disapprove_progress),
            state=state,
        )
