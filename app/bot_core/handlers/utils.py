from models.category import Category
from models.database import Session
from models.subscribes import Subscribes
from models.user import User


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
