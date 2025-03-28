import os
from dotenv import load_dotenv
load_dotenv()
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Настройка логов
logging.basicConfig(level=logging.INFO)

# Инициализация бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не указан в .env")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# Состояния формы
class Form(StatesGroup):
    fio = State()

# Обработка команды /start
@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer("Привет! Бот работает в режиме polling.")

# Запуск polling
async def main():
    logging.info("Запуск VseFormBot в режиме polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
