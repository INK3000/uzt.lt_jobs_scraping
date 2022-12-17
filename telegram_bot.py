import asyncio
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


class FSMUpdateSubs(StatesGroup):
    started = State()
    add = State()
    remove = State()


# get data from base by message.chat.id
def get_data_from_base(chat_id):
    data = dict()
    data["is_new_user"] = False
    with Session() as session:
        data["categories"] = session.query(Category).all()
        data["user"] = (
            session.query(User).filter(User.user_tg_id == chat_id).one_or_none()
        )
        if not data["user"]:
            data["user"] = User(user_tg_id=chat_id, subscribes="{}")
            session.add(data["user"])
            session.commit()
            data["is_new_user"] = True
    data["subscribes"] = Subscribes(data["user"].subscribes, data["categories"])
    return data


# welcome text for first message after start command
def get_welcome_text(data):
    if data["is_new_user"]:
        welcome_text = "You are welcome {}!"
    else:
        welcome_text = "Welcome back, {}!"
    return welcome_text


def subscribes_to_text(data: dict) -> str:
    categories_list = list(
        [
            f"{key}. {value[0]}"
            for key, value in sorted(data.items(), key=lambda i: int(i[0]))
        ]
    )
    return "\n".join(categories_list)


def report_text(subscribes: dict) -> str:
    if subscribes:
        text = f"You are subscribed to categories:\n{subscribes_to_text(subscribes)}"
    else:
        text = "You are not subscribed to any category."
    return text


def update_subscribes(text: str, data: dict, oper: str) -> dict:
    subscribes: Subscribes = data["subscribes"]
    user: User = data["user"]
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
    subscribes: Subscribes = data["subscribes"]
    await message.answer(report_text(subscribes.added))


@dp.message(Command(commands=["add"]))
async def cmd_choose_to_add_categories(
    message: types.Message, state: FSMContext
) -> None:
    data = await state.get_data()
    subscribes: Subscribes = data["subscribes"]
    if subscribes.not_added:
        await message.answer(
            f"Specify the categories you are interested in, separated by comma:\n{subscribes_to_text(subscribes.not_added)}"
        )
    else:
        await message.answer("There are no available categories.")
    await state.set_state(FSMUpdateSubs.add)


@dp.message(Command(commands=["remove"]))
async def cmd_choose_to_remove_categories(
    message: types.Message, state: FSMContext
) -> None:
    data = await state.get_data()
    subscribes: Subscribes = data["subscribes"]
    if subscribes.added:
        await message.answer(
            f"Specify the categories you want to remove, separated by comma:\n{subscribes_to_text(subscribes.added)}"
        )
    else:
        await message.answer("Yoy are not subscribed to any category.")
    await state.set_state(FSMUpdateSubs.remove)


@dp.message(FSMUpdateSubs.add)
async def cmd_add_categories(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    data = update_subscribes(text=message.text, data=data, oper="/add")
    subscribes: Subscribes = data["subscribes"]
    await message.answer(report_text(subscribes.added))
    await state.set_state(FSMUpdateSubs.started)


@dp.message(FSMUpdateSubs.remove)
async def cmd_remove_categories(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    data = update_subscribes(text=message.text, data=data, oper="/remove")
    subscribes: Subscribes = data["subscribes"]
    await message.answer(report_text(subscribes.added))
    await state.set_state(FSMUpdateSubs.started)


async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    if not is_exist_db(DATABASE_NAME):
        log_info("The database was not found. The bot will not start.")
        exit()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

# TODO При перезапуске бота, данные теряются, так как хранятся в памяти.
# Необходимо каждый раз отправлять команду /start
