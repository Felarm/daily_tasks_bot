from aiogram.fsm.state import StatesGroup, State


class DailyTaskCreationStates(StatesGroup):
    name = State()
    description = State()
    task_start_date = State()
    task_start_time = State()
    task_end_date = State()
    task_end_time = State()
    confirmation = State()


class DailyTaskCopyStates(StatesGroup):
    new_task_start_date = State()
    new_task_start_time = State()
    confirmation = State()
