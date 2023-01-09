from dataclasses import dataclass

from aiogram import BaseMiddleware
from models.database import Session
from models.subscribes import Subscribes
from models.user import User


@dataclass
class UserData:
    user: User
    subscribes: Subscribes


class LoadUser(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()
        self.users = dict()

    async def __call__(self, handler, event, data):
        user = data.get("event_from_user")
        if not self.users.get(user.id):
            self.users[user.id] = self.get_data_from_base_or_create(user)
        data["user_data"] = self.users[user.id]
        return await handler(event, data)

    @staticmethod
    def get_data_from_base_or_create(user_data):
        with Session() as session:
            user = (
                session.query(User)
                .filter(User.user_tg_id == user_data.id)
                .one_or_none()
            )
            if not user:
                user = User(
                    user_tg_id=user_data.id,
                    full_name=user_data.first_name,
                    username=user_data.username,
                    subscribes="{}",
                )
                session.add(user)
                session.commit()
        subscribes = Subscribes(user)
        return UserData(user, subscribes)
