import json

from models.database import Session
from models.category import Category
from models.user import User


class Subscribes:

    def __init__(self, subscribes_d, categories):
        self.added: dict = json.loads(subscribes_d)
        self.not_added: dict = self.get_not_added(categories)

    def __repr__(self):
        return ','.join(list(sorted(self.added)))

    def get_not_added(self, categories):
        all_categories = {
            str(category.id): category.last_id for category in categories}
        result = {key: val for key, val in all_categories.items()
                  if key not in self.added}
        return result

    def update(self, text, oper):
        to_update_list = self.text_to_list(text)
        try:
            match oper:
                case '/add':
                    self.add(to_update_list)
                case '/remove':
                    self.remove(to_update_list)
        except StopIteration as ex:
            print(f'Exception {ex}')
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
        result_list = [i.strip() for i in text.split(',')]
        return result_list


def main():
    with Session() as session:
        categories = session.query(Category).all()
        user = session.query(User).filter(User.id == 1).one_or_none()
        subscribes = Subscribes(user.subscribes, categories)
    while True:
        answer = input('...$ ')
        match answer:
            case '/add' | '/remove':
                text = input('укажите категории через запятую ')
                resp = subscribes.update(text=text, oper=answer)
                if resp:
                    user.subscribes = json.dumps(subscribes.added)
                    session.add(user)
                    session.commit()
            case '/show':
                print(subscribes)
            case '/quit':
                break


if __name__ == '__main__':
    main()
