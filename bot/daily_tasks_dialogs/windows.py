from datetime import date
from typing import Awaitable

from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Cancel, Back, Calendar, CalendarConfig, Button
from aiogram_dialog.widgets.text import Const, Format

from bot.daily_tasks_dialogs.getters import get_confirmed_new_task_info, get_confirmed_copy_task_info
from bot.daily_tasks_dialogs.handlers import cancel_creation, process_name, process_description, process_start_date, \
    process_start_time, process_end_time, process_end_date, create_confirmation, copy_confirmation, begin_approval, \
    begin_disapproval, end_approval, end_disapproval
from bot.daily_tasks_dialogs.states import DailyTaskCreationStates, DailyTaskCopyStates, DailyTaskProgressStates


class NewDailyTaskCreationWindows:
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
    def get_start_date_input_window() -> Window:
        return Window(
            Const("input start date"),
            Calendar(
                id="calendar",
                on_click=process_start_date,
                config=CalendarConfig(
                    firstweekday=0,
                    min_date=date.today()
                )
            ),
            Cancel(Const("cancel"), on_click=cancel_creation),
            Back(Const("back")),
            state=DailyTaskCreationStates.task_start_date,
        )

    @staticmethod
    def get_start_time_input_window() -> Window:
        return Window(
            Const("input start time in HH:MM format"),
            MessageInput(process_start_time),
            Cancel(Const("cancel"), on_click=cancel_creation),
            Back(Const("back")),
            state=DailyTaskCreationStates.task_start_time,
        )

    @staticmethod
    def get_end_date_input_window() -> Window:
        return Window(
            Const("input end date"),
            Calendar(
                id="calendar",
                on_click=process_end_date,
                config=CalendarConfig(
                    firstweekday=0,
                    min_date=date.today()
                )
            ),
            Cancel(Const("cancel"), on_click=cancel_creation),
            Back(Const("back")),
            state=DailyTaskCreationStates.task_end_date,
        )

    @staticmethod
    def get_end_time_input_window() -> Window:
        return Window(
            Const("input end time"),
            MessageInput(process_end_time),
            Cancel(Const("cancel"), on_click=cancel_creation),
            Back(Const("back")),
            state=DailyTaskCreationStates.task_end_time,
        )

    @staticmethod
    def get_confirmation_window() -> Window:
        return Window(
            Format("{confirm_text}"),
            Button(Const("wow, thanks"), id="confirm", on_click=create_confirmation),
            Cancel(Const("cancel"), on_click=cancel_creation),
            Back(Const("back")),
            state=DailyTaskCreationStates.confirmation,
            getter=get_confirmed_new_task_info,
        )


class CopyDailyTaskWindows:
    @staticmethod
    def get_start_date_input_window() -> Window:
        return Window(
            Const("choose date to copy"),
            Calendar(
                id="calendar",
                on_click=process_start_date,
                config=CalendarConfig(
                    firstweekday=0,
                    min_date=date.today()
                )
            ),
            Cancel(Const("cancel"), on_click=cancel_creation),
            state=DailyTaskCopyStates.new_task_start_date,
        )

    @staticmethod
    def get_start_time_input_window() -> Window:
        return Window(
            Const("input new start time in HH:MM format"),
            MessageInput(process_start_time),
            Cancel(Const("cancel"), on_click=cancel_creation),
            Back(Const("back")),
            state=DailyTaskCopyStates.new_task_start_time,
        )

    @staticmethod
    def get_confirmation_window() -> Window:
        return Window(
            Format("{confirm_text}"),
            Button(Const("yay!"), id="confirm", on_click=copy_confirmation),
            Cancel(Const("cancel"), on_click=cancel_creation),
            Back(Const("back")),
            state=DailyTaskCopyStates.confirmation,
            getter=get_confirmed_copy_task_info,
        )


class TaskBeginWindows:
    @staticmethod
    def get_task_begin_window() -> Window:
        return Window(
            Const("uhh, bruh, did u begin task?"),
            Button(Const("yup"), id="approve", on_click=begin_approval),
            Button(Const("nah, i missed somewhere in timeline"), id="disapprove", on_click=begin_disapproval),
            state=DailyTaskProgressStates.begin_state,
        )

    @staticmethod
    def get_task_end_window() -> Window:
        return Window(
            Const("bruh, did u end task?"),
            Button(Const("yup"), id="approve", on_click=end_approval),
            Button(Const("nope"), id="disapprove", on_click=end_disapproval),
            state=DailyTaskProgressStates.end_state,
        )
