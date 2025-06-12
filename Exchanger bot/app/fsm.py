from aiogram.fsm.state import State, StatesGroup


class ConvertForm(StatesGroup):
    amount = State()
    from_currency = State()
    to_currency = State()