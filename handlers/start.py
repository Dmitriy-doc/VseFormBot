from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from states.izvesh import IzveshForm
from states.otkaz import OtkazForm  # если будешь добавлять FSM для других форм

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛑 Экстренное извещение", callback_data="form_izvesh")],
        [InlineKeyboardButton(text="📄 Отказ от госпитализации", callback_data="form_otkaz")],
        # Добавишь сюда ещё кнопки, когда появятся новые формы
    ])
    await message.answer("Выберите тип справки:", reply_markup=keyboard)

@router.callback_query(F.data == "form_izvesh")
async def start_izvesh(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите ФИО пациента (полностью):")
    await state.set_state(IzveshForm.fio_patient)

@router.callback_query(F.data == "form_otkaz")
async def start_otkaz(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите ФИО пациента для отказа от госпитализации:")
    await state.set_state(OtkazForm.fio_patient)
