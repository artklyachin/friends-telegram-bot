"""
FSM состояния для бота
"""
from aiogram.fsm.state import State, StatesGroup


class CreateTestStates(StatesGroup):
    """Состояния для создания теста"""
    waiting_for_name = State()
    waiting_for_height = State()
    waiting_for_eye_color = State()
    waiting_for_fear = State()


class TakeTestStates(StatesGroup):
    """Состояния для прохождения теста"""
    waiting_for_name = State()
    waiting_for_height = State()
    waiting_for_eye_color = State()
    waiting_for_fear = State()

