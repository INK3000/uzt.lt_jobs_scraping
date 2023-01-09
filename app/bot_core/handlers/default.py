from aiogram.types import Message
from bot_core.middlewares.database import UserData


async def default(message: Message, user_data: UserData):
    await message.answer(text=user_data.user.user_tg_id)
