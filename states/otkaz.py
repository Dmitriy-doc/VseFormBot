from aiogram.fsm.state import StatesGroup, State

class OtkazForm(StatesGroup):
    fio_patient = State()
    # Добавьте дополнительные состояния, если требуется собирать дополнительные данные для отказа
