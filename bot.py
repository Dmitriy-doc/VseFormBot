import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import FSInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command
from aiogram.types import ReplyKeyboardRemove
from dotenv import load_dotenv
from docxtpl import DocxTemplate
from aiohttp import web

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 5000))

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

class RecoveryForm(StatesGroup):
    fio = State()
    birth_date = State()
    diagnosis = State()
    doctor = State()

@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await state.set_state(RecoveryForm.fio)
    await message.answer("Введите ФИО пациента:", reply_markup=ReplyKeyboardRemove())

@dp.message(RecoveryForm.fio)
async def process_fio(message: types.Message, state: FSMContext):
    await state.update_data(fio=message.text)
    await state.set_state(RecoveryForm.birth_date)
    await message.answer("Введите дату рождения пациента (ДД.ММ.ГГГГ):")

@dp.message(RecoveryForm.birth_date)
async def process_birth(message: types.Message, state: FSMContext):
    await state.update_data(birth_date=message.text)
    await state.set_state(RecoveryForm.diagnosis)
    await message.answer("Введите диагноз, с которым выздоровел пациент:")

@dp.message(RecoveryForm.diagnosis)
async def process_diagnosis(message: types.Message, state: FSMContext):
    await state.update_data(diagnosis=message.text)
    await state.set_state(RecoveryForm.doctor)
    await message.answer("Введите ФИО врача:")

@dp.message(RecoveryForm.doctor)
async def process_doctor(message: types.Message, state: FSMContext):
    await state.update_data(doctor=message.text)
    data = await state.get_data()
    await state.clear()

    doc = DocxTemplate("templates/recovery.docx")
    doc.render(data)
    filename = f"recovery_{message.from_user.id}.docx"
    doc.save(filename)
    await message.answer_document(FSInputFile(filename, filename="spravka_o_vyzdorovlenii.docx"))

@dp.message(Command("cancel"))
async def cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Отменено.")

async def main():
    await bot.set_webhook(WEBHOOK_URL)
    app = web.Application()
    dp.include_router(dp)
    app.router.add_post("/", dp.handler)
    return app

if __name__ == "__main__":
    web.run_app(main(), host="0.0.0.0", port=PORT)