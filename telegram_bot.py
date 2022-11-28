import os

from aiogram import Bot
from aiogram import Dispatcher
from aiogram import types
from aiogram.utils import executor

from models.telegram import ADMIN_TELEGRAM_USER_ID
from models.telegram import BOT_TOKEN
from models.database import DATABASE_NAME
from models.database import is_exist_db
from loggers.loggers import log_info


from models.user import User


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

if is_exist_db(DATABASE_NAME):
    log_info('База данных не найдена. Бот не будет запущен.')
    exit()


@dp.message_handler(commands=['start'])
async def command_start(message: types.Message):
    await message.answer('Я готов убивать!')


executor.start_polling(dispatcher=dp, skip_updates=True)


