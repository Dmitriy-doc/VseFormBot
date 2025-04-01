import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from docx import Document

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

TEMPLATES = {
    "Отказ от вмешательств": "templates/44_ИДС_Отказ.docx",
    "Отказ от госпитализации": "templates/49_ИДС_Отказ_госпитализации.docx",
    "Согласие на УЗИ": "templates/17_ИДС_УЗИ.docx",
    "Согласие на рентген": "templates/13_ИДС_рентген_контраст.docx"
}

class Form(StatesGroup):
    waiting_for_template = State()
    waiting_for_fio = State()
    waiting_for_birthdate = State()
    waiting_for_address = State()

@dp.message_handler(commands="start")
async def start(message: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for name in TEMPLATES:
        kb.add(KeyboardButton(name))
    await message.answer("Выберите тип документа:", reply_markup=kb)
    await Form.waiting_for_template.set()

@dp.message_handler(state=Form.waiting_for_template)
async def template_chosen(message: types.Message, state: FSMContext):
    if message.text not in TEMPLATES:
        return await message.answer("Выберите шаблон из списка.")
    await state.update_data(template=message.text)
    await message.answer("Введите ФИО:")
    await Form.next()

@dp.message_handler(state=Form.waiting_for_fio)
async def get_fio(message: types.Message, state: FSMContext):
    await state.update_data(fio=message.text)
    await message.answer("Введите дату рождения:")
    await Form.next()

@dp.message_handler(state=Form.waiting_for_birthdate)
async def get_birthdate(message: types.Message, state: FSMContext):
    await state.update_data(birthdate=message.text)
    await message.answer("Введите адрес:")
    await Form.next()

@dp.message_handler(state=Form.waiting_for_address)
async def get_address(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data["address"] = message.text

    template_path = TEMPLATES[data["template"]]
    doc = Document(template_path)
    replacements = {
        "{ФИО}": data["fio"],
        "{Дата рождения}": data["birthdate"],
        "{Адрес}": data["address"]
    }
    for p in doc.paragraphs:
        for key, val in replacements.items():
            if key in p.text:
                p.text = p.text.replace(key, val)
    out_path = f"output/{data['template'].replace(' ', '_')}_{data['fio'].replace(' ', '_')}.docx"
    os.makedirs("output", exist_ok=True)
    doc.save(out_path)

    await message.answer_document(types.InputFile(out_path))
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
