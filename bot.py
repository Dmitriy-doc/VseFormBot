import os
import asyncio
import logging
from dotenv import load_dotenv
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import (
    Message,
    FSInputFile,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from docxtpl import DocxTemplate

# Загружаем .env с токеном
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не найден в .env")

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создание бота и диспетчера
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# Состояния формы
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

# Клавиатура выбора справки
start_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Извещение", callback_data="form_recovery")],
    [InlineKeyboardButton(text="Справка о выздоровлении", callback_data="form_recovery095")],
    [InlineKeyboardButton(text="Справка в бассейн", callback_data="form_pool")],
    [InlineKeyboardButton(text="Справка в ДДУ", callback_data="form_kindergarten")],
    [InlineKeyboardButton(text="Справка в школу", callback_data="form_school")],
    [InlineKeyboardButton(text="Справка в лагерь", callback_data="form_camp")],
    [InlineKeyboardButton(text="Справка об эпидокружении", callback_data="form_epid")],
    [InlineKeyboardButton(text="Направление (057/у-04)", callback_data="form_referral")],
    [InlineKeyboardButton(text="Согласие", callback_data="form_consent")],
    [InlineKeyboardButton(text="Отказ", callback_data="form_refuse")],
])

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Выберите тип документа:", reply_markup=start_kb)

@dp.callback_query(F.data.startswith("form_"))
async def choose_form(callback: CallbackQuery, state: FSMContext):
    form_type = callback.data.replace("form_", "")
    await state.update_data(form_type=form_type)
    await state.set_state(Form.fio)
    await callback.message.edit_text("Введите ФИО пациента (полностью):")

@dp.message(Form.fio)
async def form_fio(message: Message, state: FSMContext):
    await state.update_data(fio=message.text.strip())
    await state.set_state(Form.sex)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Мужской"), KeyboardButton(text="Женский")]],
        resize_keyboard=True
    )
    await message.answer("Пол пациента:", reply_markup=keyboard)

@dp.message(Form.sex)
async def form_sex(message: Message, state: FSMContext):
    await state.update_data(sex=message.text.strip())
    await state.set_state(Form.birth)
    await message.answer("Дата рождения (ДД.ММ.ГГГГ):", reply_markup=ReplyKeyboardRemove())

@dp.message(Form.birth)
async def form_birth(message: Message, state: FSMContext):
    await state.update_data(birth=message.text.strip())
    await state.set_state(Form.address)
    await message.answer("Адрес пациента:")

@dp.message(Form.address)
async def form_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text.strip())
    await state.set_state(Form.phone)
    await message.answer("Контактный телефон:")

@dp.message(Form.phone)
async def form_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text.strip())
    await state.set_state(Form.work)
    await message.answer("Место учёбы или работы:")

@dp.message(Form.work)
async def form_work(message: Message, state: FSMContext):
    await state.update_data(work=message.text.strip())
    await state.set_state(Form.disease_date)
    await message.answer("Дата начала заболевания:")

@dp.message(Form.disease_date)
async def form_disease_date(message: Message, state: FSMContext):
    await state.update_data(disease_date=message.text.strip())
    await state.set_state(Form.consult_date)
    await message.answer("Дата обращения за мед. помощью:")

@dp.message(Form.consult_date)
async def form_consult_date(message: Message, state: FSMContext):
    await state.update_data(consult_date=message.text.strip())
    await state.set_state(Form.diagnosis_date)
    await message.answer("Дата установления диагноза:")

@dp.message(Form.diagnosis_date)
async def form_diagnosis_date(message: Message, state: FSMContext):
    await state.update_data(diagnosis_date=message.text.strip())
    await state.set_state(Form.last_visit_date)
    await message.answer("Дата последнего визита:")

@dp.message(Form.last_visit_date)
async def form_last_visit_date(message: Message, state: FSMContext):
    await state.update_data(last_visit_date=message.text.strip())
    await state.set_state(Form.diagnosis)
    await message.answer("Диагноз:")

@dp.message(Form.diagnosis)
async def form_diagnosis(message: Message, state: FSMContext):
    await state.update_data(diagnosis=message.text.strip())
    await state.set_state(Form.lab_results)
    await message.answer("Лабораторные результаты (если есть):")

@dp.message(Form.lab_results)
async def form_lab_results(message: Message, state: FSMContext):
    await state.update_data(lab_results=message.text.strip())
    await state.set_state(Form.additional_info)
    await message.answer("Дополнительные сведения (если есть):")

@dp.message(Form.additional_info)
async def form_additional_info(message: Message, state: FSMContext):
    await state.update_data(additional_info=message.text.strip())
    await state.set_state(Form.doctor_name)
    await message.answer("ФИО врача, заполнившего документ:")

@dp.message(Form.doctor_name)
async def form_doctor_name(message: Message, state: FSMContext):
    await state.update_data(doctor_name=message.text.strip())
    await state.set_state(Form.sender)
    await message.answer("ФИО отправителя (если отличается):")

@dp.message(Form.sender)
async def form_sender(message: Message, state: FSMContext):
    sender = message.text.strip()
    data = await state.update_data(sender=sender)
    await state.clear()

    data["institution"] = "ДКЦ им. Л.М. Рошаля"
    form_type = data.get("form_type", "recovery")

    template_mapping = {
        "recovery": "templates/recovery.docx",
        "recovery095": "templates/recovery_095.docx",
        "pool": "templates/pool_083.docx",
        "kindergarten": "templates/admission_ddo.docx",
        "school": "templates/admission_school.docx",
        "camp": "templates/camp_079.docx",
        "epid": "templates/epid.docx",
        "referral": "templates/referral_057.docx",
        "consent": "templates/consent.docx",
        "refuse": "templates/refuse.docx",
    }

    template_path = template_mapping.get(form_type, "templates/recovery.docx")

    try:
        doc = DocxTemplate(template_path)
        doc.render(data)
        filename = f"{form_type}_{message.from_user.id}.docx"
        doc.save(filename)
        file = FSInputFile(filename)
        await message.answer_document(file, caption="✅ Документ успешно сформирован.")
    except Exception as e:
        logging.exception("Ошибка при генерации документа")
        await message.answer("⚠️ Произошла ошибка при создании документа.")

@dp.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Ввод отменён. Чтобы начать заново, отправьте /start")

# Запуск
async def main():
    logging.info("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
