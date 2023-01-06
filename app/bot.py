import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command

from bot_core.handlers.commands import (
    cmd_set_state_to_add_categories,
    cmd_set_state_to_remove_categories,
    cmd_show_subscribe,
    cmd_start,
)
from bot_core.handlers.states import FSMUpdateSubs
from bot_core.handlers.update_subscr import (
    cmd_add_categories,
    cmd_remove_categories,
    complete_update_subscribes,
)
from create_database import create_database

import settings

bot = Bot(token=settings.BOT_TOKEN)  # pyright: ignore
dp = Dispatcher()


async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    dp.message.register(cmd_start, Command(commands=["start"]))
    dp.message.register(cmd_show_subscribe, Command(commands=["show"]))
    dp.message.register(cmd_set_state_to_add_categories, Command(commands=["add"]))
    dp.message.register(
        cmd_set_state_to_remove_categories, Command(commands=["remove"])
    )

    dp.callback_query.register(
        complete_update_subscribes, F.data == "inln_subs_key_done"
    )
    dp.callback_query.register(cmd_remove_categories, FSMUpdateSubs.remove)
    dp.callback_query.register(cmd_add_categories, FSMUpdateSubs.add)

    await dp.start_polling(bot)


if __name__ == "__main__":
    create_database()
    asyncio.run(main())

# TODO При перезапуске бота, данные теряются, так как хранятся в памяти.
# Необходимо каждый раз отправлять команду /start
