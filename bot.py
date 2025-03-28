import os
from dotenv import load_dotenv
load_dotenv()

import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message, FSInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart, Command
from aiohttp import web
from docxtpl import DocxTemplate

# Логирование
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logfile_handler = logging.FileHandler("notifications_log.txt", encoding="utf-8")
logfile_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
logfile_handler.setFormatter(formatter)
logging.getLogger().addHandler(logfile_handler)

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 5000))

if not BOT_TOKEN or not WEBHOOK_URL:
    raise RuntimeError("Не указан BOT_TOKEN или WEBHOOK_URL в .env")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
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
    await message.answer("Введите ФИО пациента:")


@dp.message(Form.fio)
async def process_fio(message: Message, state: FSMContext):
    await state.update_data(fio=message.text)
    await state.set_state(Form.sex)
    await message.answer("Пол пациента (Мужской/Женский):")


@dp.message(Form.sex)
async def process_sex(message: Message, state: FSMContext):
    await state.update_data(sex=message.text)
    await state.set_state(Form.birth)
    await message.answer("Дата рождения пациента (ДД.ММ.ГГГГ):")


@dp.message(Form.birth)
async def process_birth(message: Message, state: FSMContext):
    await state.update_data(birth=message.text)
    await state.set_state(Form.address)
    await message.answer("Адрес пациента:")


@dp.message(Form.address)
async def process_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(Form.phone)
    await message.answer("Телефон пациента:")


@dp.message(Form.phone)
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(Form.work)
    await message.answer("Место работы/учёбы пациента:")


@dp.message(Form.work)
async def process_work(message: Message, state: FSMContext):
    await state.update_data(work=message.text)
    await state.set_state(Form.disease_date)
    await message.answer("Дата заболевания:")


@dp.message(Form.disease_date)
async def process_disease_date(message: Message, state: FSMContext):
    await state.update_data(disease_date=message.text)
    await state.set_state(Form.consult_date)
    await message.answer("Дата обращения за медпомощью:")


@dp.message(Form.consult_date)
async def process_consult_date(message: Message, state: FSMContext):
    await state.update_data(consult_date=message.text)
    await state.set_state(Form.diagnosis_date)
    await message.answer("Дата установления диагноза:")


@dp.message(Form.diagnosis_date)
async def process_diagnosis_date(message: Message, state: FSMContext):
    await state.update_data(diagnosis_date=message.text)
    await state.set_state(Form.last_visit_date)
    await message.answer("Дата последнего визита пациента:")


@dp.message(Form.last_visit_date)
async def process_last_visit_date(message: Message, state: FSMContext):
    await state.update_data(last_visit_date=message.text)
    await state.set_state(Form.diagnosis)
    await message.answer("Диагноз пациента:")


@dp.message(Form.diagnosis)
async def process_diagnosis(message: Message, state: FSMContext):
    await state.update_data(diagnosis=message.text)
    await state.set_state(Form.lab_results)
    await message.answer("Лабораторные результаты (если есть):")


@dp.message(Form.lab_results)
async def process_lab_results(message: Message, state: FSMContext):
    await state.update_data(lab_results=message.text)
    await state.set_state(Form.additional_info)
    await message.answer("Доп. сведения (если есть):")


@dp.message(Form.additional_info)
async def process_additional_info(message: Message, state: FSMContext):
    await state.update_data(additional_info=message.text)
    await state.set_state(Form.doctor_name)
    await message.answer("ФИО врача, заполнившего извещение:")


@dp.message(Form.doctor_name)
async def process_doctor_name(message: Message, state: FSMContext):
    await state.update_data(doctor_name=message.text)
    await state.set_state(Form.sender)
    await message.answer("ФИО отправителя извещения (если отличается):")


@dp.message(Form.sender)
async def process_sender(message: Message, state: FSMContext):
    sender = message.text
    data = await state.update_data(sender=sender)
    await state.clear()

    data["institution"] = "ДКЦ им. Л.М. Рошаля"

    try:
        doc = DocxTemplate("templates/recovery.docx")
        doc.render(data)
        output_file = f"notification_{message.from_user.id}.docx"
        doc.save(output_file)

        file = FSInputFile(output_file)
        await message.answer_document(file, caption="✅ Документ сформирован.")

        log_entry = f"{datetime.now()} - @{message.from_user.username or 'Без username'} - {data['fio']} - {data['diagnosis']}"
        logging.info(log_entry)
    except Exception as e:
        logging.exception("Ошибка при формировании документа")
        await message.answer("⚠️ Ошибка при создании документа.")


@dp.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("✅ Заполнение отменено. Введите /start чтобы начать заново.")


async def main():
    logging.info("🚀 Запуск бота...")
    await bot.set_webhook(WEBHOOK_URL)

    app = web.Application()
    app.router.add_post("/", dp.as_handler())

    return app


if __name__ == "__main__":
    web.run_app(main(), host="0.0.0.0", port=PORT)
