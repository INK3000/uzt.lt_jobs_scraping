import json

from models.category import Category


class Subscribes:

    """
    class for users subscribes
    for init need subscribes@dp.message(Command(commands=['show']))
    """

    # subscribes_d: '{"6": 1234, "3": 2332}'
    # categories: [Category, ...]
    # Category: id, name, event_target, last_id

    def __init__(self, subscribes: str, categories: list[Category]):
        self.added = dict()
        self.not_added = dict()
        for category in categories:
            value = (category.name, category.last_id)
            if str(category.id) in json.loads(subscribes):
                self.added[str(category.id)] = value
            else:
                self.not_added[str(category.id)] = value

    @property
    def json_data(self):
        data = {key: value[1] for key, value in sorted(self.added.items())}
        return json.dumps(data)

    def __repr__(self):
        # TODO сделать чтобы правильно отображались номера категорий и их имена
        # 1. Компьютеры/ИТ  --- category.id category.name \n
        categories_list = list(
            [f"{key}. {value[0]}" for key, value in sorted(self.added.items())]
        )
        return "\n".join(categories_list)

    def __bool__(self):
        return bool(self.added)

    def update(self, text, oper):
        to_update_list = self.text_to_list(text)
        try:
            match oper:
                case "/add":
                    self.add(to_update_list)
                case "/remove":
                    self.remove(to_update_list)
        except Exception as ex:
            print(f"Exception {ex}")
            return False
        return True

    def remove(self, to_add_list):
        for key in to_add_list:
            value = self.added.pop(key, False)
            if value:
                self.not_added.update({key: value})

    def add(self, to_add_list):
        for key in to_add_list:
            value = self.not_added.pop(key, False)
            if value:
                self.added.update({key: value})

    @staticmethod
    def text_to_list(text):
        result_list = [i.strip() for i in text.split(",")]
        return result_list
