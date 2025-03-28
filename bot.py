import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, FSInputFile, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from docxtpl import DocxTemplate

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не найден в .env")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

class Form(StatesGroup):
    fio = State()
    sex = State()
    birth = State()
    address = State()
    phone = State()
    work = State()
    disease_date = State()
    consult_date = State()
    diagnosis_date = State()
    last_visit_date = State()
    diagnosis = State()
    lab_results = State()
    additional_info = State()
    doctor_name = State()
    sender = State()

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(Form.fio)
    await message.answer("Введите ФИО пациента (полностью):", reply_markup=ReplyKeyboardRemove())

@dp.message(Form.fio)
async def process_fio(message: Message, state: FSMContext):
    await state.update_data(fio=message.text.strip())
    await state.set_state(Form.sex)
    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Мужской"), KeyboardButton(text="Женский")]], resize_keyboard=True)
    await message.answer("Пол пациента:", reply_markup=keyboard)

@dp.message(Form.sex)
async def process_sex(message: Message, state: FSMContext):
    await state.update_data(sex=message.text.strip())
    await state.set_state(Form.birth)
    await message.answer("Дата рождения (ДД.ММ.ГГГГ):", reply_markup=ReplyKeyboardRemove())

@dp.message(Form.birth)
async def process_birth(message: Message, state: FSMContext):
    await state.update_data(birth=message.text.strip())
    await state.set_state(Form.address)
    await message.answer("Адрес пациента:")

@dp.message(Form.address)
async def process_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text.strip())
    await state.set_state(Form.phone)
    await message.answer("Контактный телефон:")

@dp.message(Form.phone)
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text.strip())
    await state.set_state(Form.work)
    await message.answer("Место учёбы или работы:")

@dp.message(Form.work)
async def process_work(message: Message, state: FSMContext):
    await state.update_data(work=message.text.strip())
    await state.set_state(Form.disease_date)
    await message.answer("Дата начала заболевания:")

@dp.message(Form.disease_date)
async def process_disease_date(message: Message, state: FSMContext):
    await state.update_data(disease_date=message.text.strip())
    await state.set_state(Form.consult_date)
    await message.answer("Дата обращения за мед. помощью:")

@dp.message(Form.consult_date)
async def process_consult_date(message: Message, state: FSMContext):
    await state.update_data(consult_date=message.text.strip())
    await state.set_state(Form.diagnosis_date)
    await message.answer("Дата установления диагноза:")

@dp.message(Form.diagnosis_date)
async def process_diagnosis_date(message: Message, state: FSMContext):
    await state.update_data(diagnosis_date=message.text.strip())
    await state.set_state(Form.last_visit_date)
    await message.answer("Дата последнего визита:")

@dp.message(Form.last_visit_date)
async def process_last_visit_date(message: Message, state: FSMContext):
    await state.update_data(last_visit_date=message.text.strip())
    await state.set_state(Form.diagnosis)
    await message.answer("Диагноз:")

@dp.message(Form.diagnosis)
async def process_diagnosis(message: Message, state: FSMContext):
    await state.update_data(diagnosis=message.text.strip())
    await state.set_state(Form.lab_results)
    await message.answer("Лабораторные результаты (если есть):")

@dp.message(Form.lab_results)
async def process_lab_results(message: Message, state: FSMContext):
    await state.update_data(lab_results=message.text.strip())
    await state.set_state(Form.additional_info)
    await message.answer("Дополнительные сведения (если есть):")

@dp.message(Form.additional_info)
async def process_additional_info(message: Message, state: FSMContext):
    await state.update_data(additional_info=message.text.strip())
    await state.set_state(Form.doctor_name)
    await message.answer("ФИО врача, заполнившего извещение:")

@dp.message(Form.doctor_name)
async def process_doctor_name(message: Message, state: FSMContext):
    await state.update_data(doctor_name=message.text.strip())
    await state.set_state(Form.sender)
    await message.answer("ФИО отправителя извещения (если отличается):")

@dp.message(Form.sender)
async def process_sender(message: Message, state: FSMContext):
    sender = message.text.strip()
    data = await state.update_data(sender=sender)
    await state.clear()
    data["institution"] = "ДКЦ им. Л.М. Рошаля"

    try:
        doc = DocxTemplate("templates/recovery.docx")
        doc.render(data)
        filename = f"izvesh_{message.from_user.id}.docx"
        doc.save(filename)
        file = FSInputFile(filename)
        await message.answer_document(file, caption="✅ Извещение сформировано.")
    except Exception as e:
        logging.exception("Ошибка при формировании документа")
        await message.answer("Произошла ошибка при создании документа.")

@dp.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Отменено. Чтобы начать заново — /start")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
