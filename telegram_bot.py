from aiogram import Bot
from aiogram import Dispatcher
from aiogram import types
from aiogram.utils import executor

import json

from models.telegram import ADMIN_TELEGRAM_USER_ID
from models.telegram import BOT_TOKEN
from models.database import DATABASE_NAME
from models.database import is_exist_db
from loggers.loggers import log_info
from models.database import Session
from models.category import Category
from models.user import User


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
categories = None

@dp.message_handler(commands=['start'])
async def command_start(message: types.Message):
    user_tg_id = message.chat.id
    text = f'Choose interesting categories \n{categories}'
    with Session() as session:
        user = session.query(User).filter(User.user_tg_id == user_tg_id).all()
        if not user:
            session.add(User(user_tg_id=user_tg_id))
            session.commit()
            await message.answer(f'You are welcome!\n\n{text}')
        else:
            await message.answer(f'You are already started\n\n{text}')


# @dp.message_handler(commands=['subscribe'])
# async def command_start(message: types.Message):
#     user_tg_id = message.chat.id
#     categories_to_subscribe = [i.strip() for i in "1, 2,3 ".split(',')]
#     with Session() as session:
#         user = session.query(User).filter(User.user_tg_id ==user_tg_id).one_or_none()
#         subscribes = {category.id: category.last_id for category in session.query(Category).filter(Category.id.in_(categories_to_subscribe)).all()}
#         if user:
#             user.subscribes = json.dumps(subscribes)
#             session.add(user)
#             session.commit()
#             await message.answer(f'You are subscribed!')

def main():
    if not is_exist_db(DATABASE_NAME):
        log_info('База данных не найдена. Бот не будет запущен.')
        exit()
    with Session() as session:
        global categories
        categories = session.query(Category.id, Category.name).order_by(Category.id).all()
        categories = '\n'.join([f'{idx}: {name}' for idx, name in categories])

    executor.start_polling(dispatcher=dp, skip_updates=True)


if __name__ == '__main__':
    main()

