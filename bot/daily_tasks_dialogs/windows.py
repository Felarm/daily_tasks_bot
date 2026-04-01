from datetime import date
from typing import Awaitable

from aiogram.fsm.state import State
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Cancel, Back, Calendar, CalendarConfig, Button
from aiogram_dialog.widgets.text import Const, Format

from bot.daily_tasks_dialogs.handlers import cancel_creation, process_name, process_description, create_confirmation, \
    approve_progress, disapprove_progress, process_time_period, process_date_period, delay_progress
from bot.daily_tasks_dialogs.states import DailyTaskCreationStates


class DailyTaskCreationWindows:
    @staticmethod
    def get_name_input_window() -> Window:
        return Window(
            Const("input task name"),
            MessageInput(process_name),
            Cancel(Const("cancel"), on_click=cancel_creation),
            state=DailyTaskCreationStates.name,
        )

    @staticmethod
    def get_description_input_window() -> Window:
        return Window(
            Const("input task description"),
            MessageInput(process_description),
            Cancel(Const("cancel"), on_click=cancel_creation),
            Back(Const("back")),
            state=DailyTaskCreationStates.description,
        )

    @staticmethod
    def get_date_input_window(header: str, calendar_id: str, state: State) -> Window:
        return Window(
            Const(header),
            Calendar(
                id=calendar_id,
                on_click=process_date_period,
                config=CalendarConfig(
                    firstweekday=0,
                    min_date=date.today()
                )
            ),
            Cancel(Const("cancel"), on_click=cancel_creation),
            Back(Const("back")),
            state=state,
        )

    @staticmethod
    def get_time_input_window(header: str, msg_input_id: str, state: State) -> Window:
        return Window(
            Const(header),
            MessageInput(process_time_period, id=msg_input_id),
            Cancel(Const("cancel"), on_click=cancel_creation),
            Back(Const("back")),
            state=state,
        )

    @staticmethod
    def get_confirmation_window(action_id: str, state: State, getter: Awaitable) -> Window:
        return Window(
            Format("{confirm_text}"),
            Button(Const("wow, thanks"), id=action_id, on_click=create_confirmation),
            Cancel(Const("cancel"), on_click=cancel_creation),
            Back(Const("back")),
            state=state,
            getter=getter,
        )


class TaskProgressWindows:
    @staticmethod
    def get_task_progress_window(header: str, approve_id: str, delay_id: str, disapprove_id: str, state: State) -> Window:
        return Window(
            Const(header),
            Button(Const("yup"), id=approve_id, on_click=approve_progress),
            Button(Const("not yet"), id=delay_id, on_click=delay_progress),
            Button(Const("nope"), id=disapprove_id, on_click=disapprove_progress),
            state=state,
        )
