import os
import asyncio
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import (
    Message, CallbackQuery, FSInputFile,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from docxtpl import DocxTemplate

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не найден в .env")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

# Состояния
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

# Кнопки справок
start_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Извещение", callback_data="form_recovery")],
    [InlineKeyboardButton(text="Справка о выздоровлении", callback_data="form_recovery095")],
    [InlineKeyboardButton(text="Справка в бассейн", callback_data="form_pool")],
    [InlineKeyboardButton(text="Справка в ДДУ", callback_data="form_kindergarten")],
    [InlineKeyboardButton(text="Справка в школу", callback_data="form_school")],
    [InlineKeyboardButton(text="Справка в лагерь", callback_data="form_camp")],
    [InlineKeyboardButton(text="Справка об эпидокружении", callback_data="form_epid")],
    [InlineKeyboardButton(text="Направление", callback_data="form_referral")],
    [InlineKeyboardButton(text="Согласие", callback_data="form_consent")],
    [InlineKeyboardButton(text="Отказ от госпитализации", callback_data="form_refuse")],
])

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Выберите тип документа:", reply_markup=start_kb)

@dp.callback_query(F.data.startswith("form_"))
async def choose_form(callback: CallbackQuery, state: FSMContext):
    form_type = callback.data.replace("form_", "")
    await state.update_data(form_type=form_type)
    await state.set_state(Form.fio)
    await callback.message.edit_text("Введите ФИО пациента (полностью):")

@dp.message(Form.fio)
async def process_fio(message: Message, state: FSMContext):
    await state.update_data(fio=message.text)
    await state.set_state(Form.sex)
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Мужской"), KeyboardButton(text="Женский")]],
        resize_keyboard=True
    )
    await message.answer("Пол пациента:", reply_markup=kb)

@dp.message(Form.sex)
async def process_sex(message: Message, state: FSMContext):
    await state.update_data(sex=message.text)
    await state.set_state(Form.birth)
    await message.answer("Дата рождения (ДД.ММ.ГГГГ):", reply_markup=ReplyKeyboardRemove())

@dp.message(Form.birth)
async def process_birth(message: Message, state: FSMContext):
    await state.update_data(birth=message.text)
    await state.set_state(Form.address)
    await message.answer("Адрес пациента:")

@dp.message(Form.address)
async def process_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(Form.phone)
    await message.answer("Контактный телефон:")

@dp.message(Form.phone)
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(Form.work)
    await message.answer("Место учёбы или работы:")

@dp.message(Form.work)
async def process_work(message: Message, state: FSMContext):
    await state.update_data(work=message.text)
    await state.set_state(Form.disease_date)
    await message.answer("Дата начала заболевания:")

@dp.message(Form.disease_date)
async def process_disease_date(message: Message, state: FSMContext):
    await state.update_data(disease_date=message.text)
    await state.set_state(Form.consult_date)
    await message.answer("Дата обращения за мед. помощью:")

@dp.message(Form.consult_date)
async def process_consult_date(message: Message, state: FSMContext):
    await state.update_data(consult_date=message.text)
    await state.set_state(Form.diagnosis_date)
    await message.answer("Дата установления диагноза:")

@dp.message(Form.diagnosis_date)
async def process_diagnosis_date(message: Message, state: FSMContext):
    await state.update_data(diagnosis_date=message.text)
    await state.set_state(Form.last_visit_date)
    await message.answer("Дата последнего визита:")

@dp.message(Form.last_visit_date)
async def process_last_visit_date(message: Message, state: FSMContext):
    await state.update_data(last_visit_date=message.text)
    await state.set_state(Form.diagnosis)
    await message.answer("Диагноз:")

@dp.message(Form.diagnosis)
async def process_diagnosis(message: Message, state: FSMContext):
    await state.update_data(diagnosis=message.text)
    await state.set_state(Form.lab_results)
    await message.answer("Лабораторные результаты (если есть):")

@dp.message(Form.lab_results)
async def process_lab_results(message: Message, state: FSMContext):
    await state.update_data(lab_results=message.text)
    await state.set_state(Form.additional_info)
    await message.answer("Дополнительные сведения (если есть):")

@dp.message(Form.additional_info)
async def process_additional_info(message: Message, state: FSMContext):
    await state.update_data(additional_info=message.text)
    await state.set_state(Form.doctor_name)
    await message.answer("ФИО врача, заполнившего документ:")

@dp.message(Form.doctor_name)
async def process_doctor_name(message: Message, state: FSMContext):
    await state.update_data(doctor_name=message.text)
    await state.set_state(Form.sender)
    await message.answer("ФИО отправителя (если отличается):")

@dp.message(Form.sender)
async def process_sender(message: Message, state: FSMContext):
    sender = message.text
    data = await state.update_data(sender=sender)
    await state.clear()
    data["institution"] = "ДКЦ им. Л.М. Рошаля"

    form_type = data.get("form_type", "recovery")
    template_paths = {
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
    template_path = template_paths.get(form_type)

    try:
        doc = DocxTemplate(template_path)
        doc.render(data)
        filename = f"{form_type}_{message.from_user.id}.docx"
        doc.save(filename)
        await message.answer_document(FSInputFile(filename), caption="✅ Документ готов.")
    except Exception as e:
        logging.exception("Ошибка генерации документа")
        await message.answer("❌ Ошибка при создании документа.")

@dp.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Ввод отменён. Чтобы начать заново — /start", reply_markup=ReplyKeyboardRemove())

async def main():
    logging.info("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
