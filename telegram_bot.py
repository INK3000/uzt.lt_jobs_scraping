import asyncio
import logging
import sys

import json

from aiogram import Bot
from aiogram import Dispatcher
from aiogram import F
from aiogram import Router
from aiogram.filters import Command, Text
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import ReplyKeyboardRemove
from aiogram.types import KeyboardButton


from models.telegram import BOT_TOKEN
from models.database import DATABASE_NAME
from models.database import is_exist_db
from models.database import Session
from models.category import Category
from models.user import User
from models.subscribes import Subscribes

from loggers.loggers import log_info


bot = Bot(token=BOT_TOKEN)  # pyright: ignore
dp = Dispatcher()
init_router = Router()


class FSMUpdateSubs(StatesGroup):
    started = State()
    add = State()
    remove = State()


def update_subscribes(text: str, data: dict, oper: str) -> dict:
    subscribes = data['subscribes']
    user = data['user']
    response = subscribes.update(text=text, oper=oper)
    if response:
        with Session() as session:
            user.subscribes = json.dumps(subscribes.added)
            session.add(user)
            session.commit()
    return data


@dp.message(Command(commands=['start']))
async def cmd_start(message: types.Message, state: FSMContext):
    user_tg_id = message.chat.id
    user_name = message.chat.username
    with Session() as session:
        categories = session.query(Category).all()
        user = session.query(User).filter(
            User.user_tg_id == user_tg_id).one_or_none()

        if not user:
            session.add(User(user_tg_id=user_tg_id))
            session.commit()
            await message.answer(f'You are welcome, {user_name}!')
        else:
            await message.answer(f'You are already started, {user_name}')

        subscribes = Subscribes(json.loads(user.subscribes), categories)

        await state.set_state(FSMUpdateSubs.started)
        await state.set_data({
            'user': user,
            'categories': categories,
            'subscribes': subscribes,
        })
        await message.answer(text='What you want to do?',
                             reply_markup=ReplyKeyboardMarkup(
                                 keyboard=[
                                     [
                                         KeyboardButton(
                                             text='Show my subscribes'),
                                         KeyboardButton(
                                             text='Add to my subscribes'),
                                         KeyboardButton(
                                             text='Remove from my subscribes')
                                     ]
                                 ],
                                 one_time_keyboard=True,
                                 resize_keyboard=True

                             ))


@dp.message(Command(commands=['show']))
@dp.message(Text(text='Show my subscribes'))
async def cmd_show(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    subscribes = data['subscribes']
    print(bool(subscribes), type(subscribes))
    if subscribes:
        text = f'Вы подписаны на категории: {subscribes}'
    else:
        text = 'Вы не подписаны ни на одну категорию.'
    await message.answer(text)


@dp.message(Command(commands=['add']))
@dp.message(Text(text='Add to my subscribes'))
async def cmd_choose_to_add_categories(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    categories = data['categories']
    text = '\n'.join(
        [f'{category.id}: {category.name}' for category in categories])
    await message.answer(text)
    await message.answer('Укажите через запятую интересующие вас категории:')
    await state.set_state(FSMUpdateSubs.add)


@dp.message(Command(commands=['remove']))
@dp.message(Text(text='Remove from my subscribes'))
async def cmd_choose_to_remove_categories(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    text = f'Вы подписаны на категории: {data["subscribes"]}'
    await message.answer(text)
    await message.answer(f'Укажите через запятую категории, которые хотите удалить из своей подписки:')
    await state.set_state(FSMUpdateSubs.remove)


@dp.message(FSMUpdateSubs.add)
async def cmd_add_categories(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    data = update_subscribes(text=message.text, data=data, oper='/add')
    await message.answer(f'Теперь вы подписаны на категории: {data["subscribes"]}')
    await state.set_state(FSMUpdateSubs.started)


@dp.message(FSMUpdateSubs.remove)
async def cmd_remove_categories(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    data = update_subscribes(text=message.text, data=data, oper='/remove')
    await message.answer(f'Теперь вы подписаны на категории: {data["subscribes"]}')
    await state.set_state(FSMUpdateSubs.started)


async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    if not is_exist_db(DATABASE_NAME):
        log_info('База данных не найдена. Бот не будет запущен.')
        exit()
    dp.include_router(init_router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

# TODO При перезапуске бота, данные теряются, так как хранятся в памяти.
# Необходимо каждый раз отправлять команду /start
