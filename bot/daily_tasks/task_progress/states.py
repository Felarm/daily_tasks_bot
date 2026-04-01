from aiogram.fsm.state import StatesGroup, State


class DailyTaskProgressStates(StatesGroup):
    begin_state = State()
    end_state = State()
