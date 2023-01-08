import json
from models.database import Session
from models.user import User
from models.category import Category


class Subscribes:

    """
    class for users subscribes
    """

    # subscribes_d: '{"6": 1234, "3": 2332}'
    # categories: [Category, ...]
    # Category: id, name, event_target, last_id

    def __init__(self, user: User):
        self.user: User = user
        self._added = dict()
        self._not_added = dict()
        self.init_subscribes()

    @property
    def added(self):
        if not self._added and not self._not_added:
            self.init_subscribes()
        return self._added

    @property
    def not_added(self):
        if not self._added and not self._not_added:
            self.init_subscribes()
        return self._not_added

    @property
    def json_data(self):
        data = {
            key: value[1]
            for key, value in sorted(self._added.items(), key=lambda i: int(i[0]))
        }
        return json.dumps(data)

    def __repr__(self):
        categories_list = list(
            [
                f"{key}. {value[0]}"
                for key, value in sorted(self._added.items(), key=lambda i: int(i[0]))
            ]
        )
        return "\n".join(categories_list)

    def __bool__(self):
        return bool(self._added)

    def update(self, category_id, oper):
        try:
            match oper:
                case "/add":
                    self.add(category_id)
                case "/remove":
                    self.remove(category_id)
        except Exception as ex:
            print(f"Exception {ex}")
            return False
        return True

    def remove(self, category_id):
        value = self._added.pop(category_id, False)
        if value:
            self._not_added.update({category_id: value})

    def add(self, category_id):
        value = self._not_added.pop(category_id, False)
        if value:
            self._added.update({category_id: value})

    @staticmethod
    def get_categories_from_base():
        with Session() as session:
            categories = session.query(Category).all()
        return categories

    def init_subscribes(self):
        categories = self.get_categories_from_base()
        for category in categories:
            key = category.id
            value = (category.name, category.last_id)
            if str(key) in json.loads(self.user.subscribes):
                self._added[key] = value
            else:
                self._not_added[key] = value
