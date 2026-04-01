from datetime import date
from typing import Awaitable

from aiogram.fsm.state import State
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Cancel, Back, Calendar, CalendarConfig, Button
from aiogram_dialog.widgets.text import Const, Format

from bot.daily_tasks.new_tasks_creation.handlers import process_name, cancel_creation, process_description, \
    process_date_period, process_time_period, create_confirmation
from bot.daily_tasks.new_tasks_creation.states import DailyTaskCreationStates


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
