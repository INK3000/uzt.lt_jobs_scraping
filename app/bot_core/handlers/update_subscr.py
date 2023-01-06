from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot_core.handlers.states import FSMUpdateSubs
from bot_core.handlers.utils import report_text
from bot_core.keyboards.add_remove_subscr import get_add_remove_inline_keyboard
from models.database import Session
from models.subscribes import Subscribes
from models.user import User


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


async def complete_update_subscribes(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    subscribes: Subscribes = data["subscribes"]
    await query.answer()
    await query.message.delete()
    await query.message.answer(report_text(subscribes.added))
    await state.set_state(FSMUpdateSubs.started)


async def cmd_remove_categories(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    text = query.data.split("_")[-1]
    data = update_subscribes(text=text, data=data, oper="/remove")
    await query.answer()
    await query.message.delete()
    subscribes: Subscribes = data["subscribes"]
    if subscribes.added:
        await query.message.answer(
            "Select the categories you want to remove\
                    \nfrom your subscriptions by clicking on the category name buttons.\
                    \nWhen you're done selecting, click the 'Complete' button\
                    \nto save your changes",
            reply_markup=get_add_remove_inline_keyboard(subscribes.added),
        )
    else:
        await query.message.answer("There are no available categories.")


async def cmd_add_categories(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    text = query.data.split("_")[-1]
    data = update_subscribes(text=text, data=data, oper="/add")
    await query.answer()
    await query.message.delete()
    subscribes: Subscribes = data["subscribes"]
    if subscribes.not_added:
        await query.message.answer(
            "Select the categories you are interested in\
            \nby clicking on the category buttons.\
            \nOnce you've selected the categories you want,\
            \nclick the 'Complete' button\
            \nto save your changes.",
            reply_markup=get_add_remove_inline_keyboard(subscribes.not_added),
        )
    else:
        await query.message.answer("There are no available categories.")
