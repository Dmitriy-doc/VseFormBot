from aiogram.fsm.state import StatesGroup, State

class IzveshForm(StatesGroup):
    fio_patient = State()
    # Добавьте другие состояния, если необходимо (например, для сбора дополнительных данных)
