import asyncio
import json
import logging
import sys

from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from loggers.loggers import log_info
from models.category import Category
from models.database import DATABASE_NAME, Session, is_exist_db
from models.subscribes import Subscribes
from models.telegram import BOT_TOKEN
from models.user import User

bot = Bot(token=BOT_TOKEN)  # pyright: ignore
dp = Dispatcher()
init_router = Router()


class FSMUpdateSubs(StatesGroup):
    started = State()
    add = State()
    remove = State()


# welcome text for first message after start command
def get_welcome_text(data):
    if data["is_new_user"]:
        welcome_text = "You are welcome {}!"
    else:
        welcome_text = "Welcome back, {}!"
    return welcome_text


def get_data_from_base(user_tg_id):
    data = dict()
    data["is_new_user"] = False
    with Session() as session:
        data["categories"] = session.query(Category).all()
        data["user"] = (
            session.query(User).filter(User.user_tg_id == user_tg_id).one_or_none()
        )
        if not data["user"]:
            data["user"] = User(user_tg_id=user_tg_id, subscribes="{}")
            session.add(data["user"])
            session.commit()
            data["is_new_user"] = True
    data["subscribes"] = Subscribes(data["user"].subscribes, data["categories"])
    return data


def subscribes_to_text(subscribes: Subscribes) -> str:
    if subscribes:
        text = f"You are subscribed to categories:\n{subscribes}"
    else:
        text = "You are not subscribed to any category."
    return text


def update_subscribes(text: str, data: dict, oper: str) -> dict:
    subscribes: Subscribes = data["subscribes"]
    user = data["user"]
    response = subscribes.update(text=text, oper=oper)
    if response:
        user.subscribes = subscribes.json_data
        with Session() as session:
            session.add(user)
            session.commit()
    return data


@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message, state: FSMContext):
    data = get_data_from_base(message.chat.id)

    await state.set_state(FSMUpdateSubs.started)
    await state.set_data(data)

    await message.answer(text=get_welcome_text(data).format(message.chat.username))
    await message.answer(
        text="/start - if something wrong - try start again \n"
        "/add - add categories to my subscribes\n"
        "/remove - remove categories from my subscribes\n"
        "/show - show my subscribes"
    )


@dp.message(Command(commands=["show"]))
async def cmd_show(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    subscribes = data["subscribes"]
    await message.answer(subscribes_to_text(subscribes))


@dp.message(Command(commands=["add"]))
async def cmd_choose_to_add_categories(
    message: types.Message, state: FSMContext
) -> None:
    data = await state.get_data()
    categories = data["categories"]
    text = "\n".join([f"{category.id}: {category.name}" for category in categories])
    await message.answer(text)
    await message.answer(
        "Specify the categories you are interested in, separated by commas:"
    )
    await state.set_state(FSMUpdateSubs.add)


@dp.message(Command(commands=["remove"]))
async def cmd_choose_to_remove_categories(
    message: types.Message, state: FSMContext
) -> None:
    data = await state.get_data()
    await message.answer(subscribes_to_text(data["subscribes"]))
    await message.answer(
        "Specify the categories you want to remove "
        "from your subscription, separated by commas:"
    )
    await state.set_state(FSMUpdateSubs.remove)


@dp.message(FSMUpdateSubs.add)
async def cmd_add_categories(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    data = update_subscribes(text=message.text, data=data, oper="/add")
    await message.answer(subscribes_to_text(data["subscribes"]))
    await state.set_state(FSMUpdateSubs.started)


@dp.message(FSMUpdateSubs.remove)
async def cmd_remove_categories(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    data = update_subscribes(text=message.text, data=data, oper="/remove")
    await message.answer(subscribes_to_text(data["subscribes"]))
    await state.set_state(FSMUpdateSubs.started)


async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    if not is_exist_db(DATABASE_NAME):
        log_info("The database was not found. The bot will not start.")
        exit()
    dp.include_router(init_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

# TODO При перезапуске бота, данные теряются, так как хранятся в памяти.
# Необходимо каждый раз отправлять команду /start
