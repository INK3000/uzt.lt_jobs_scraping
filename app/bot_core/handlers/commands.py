from aiogram import types
from aiogram.fsm.context import FSMContext

from bot_core.handlers.states import FSMUpdateSubs
from bot_core.handlers.utils import get_data_from_base, get_welcome_text, report_text
from bot_core.keyboards.add_remove_subscr import get_add_remove_inline_keyboard
from models.subscribes import Subscribes


async def cmd_start(message: types.Message, state: FSMContext):
    data = get_data_from_base(message)

    await state.set_state(FSMUpdateSubs.started)
    await state.set_data(data)

    await message.answer(text=get_welcome_text(data).format(message.chat.username))
    await message.answer(
        text="/start - if something wrong - try start again \n"
        "/add - add categories to my subscribes\n"
        "/remove - remove categories from my subscribes\n"
        "/show - show my subscribes"
    )


async def cmd_show_subscribe(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    subscribes: Subscribes = data["subscribes"]
    await message.answer(report_text(subscribes.added))


async def cmd_set_state_to_add_categories(
    message: types.Message, state: FSMContext
) -> None:
    data = await state.get_data()
    subscribes: Subscribes = data["subscribes"]
    if subscribes.not_added:
        await message.answer(
            "Select the categories you are interested in\
            \nby clicking on the category buttons.\
            \nOnce you've selected the categories you want,\
            \nclick the '>>> Complete <<<' button\
            \nto save your changes.",
            reply_markup=get_add_remove_inline_keyboard(subscribes.not_added),
        )
    else:
        await message.answer("There are no available categories.")
    await state.set_state(FSMUpdateSubs.add)


async def cmd_set_state_to_remove_categories(
    message: types.Message, state: FSMContext
) -> None:
    data = await state.get_data()
    subscribes: Subscribes = data["subscribes"]
    if subscribes.added:
        await message.answer(
            "Select the categories you want to remove\
                    \nfrom your subscriptions by clicking on the category name buttons.\
                    \nWhen you're done selecting, click the '>>> Complete <<<' button\
                    \nto save your changes",
            reply_markup=get_add_remove_inline_keyboard(subscribes.added),
        )
    else:
        await message.answer("There are no available categories.")
    await state.set_state(FSMUpdateSubs.remove)
