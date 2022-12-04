from models.category import Category


class Subscribes():

    '''
    class for users subscribes
    for init need subscribes@dp.message(Command(commands=['show']))
    '''
    # subscribes_d: {"6": 1234, "3": 2332}
    # categories: [Category, ...]
    # Category: id, name, event_target, last_id

    def __init__(self, subscribes_d: dict, categories: list[Category]):
        self.added = subscribes_d
        self.not_added: dict = self.get_not_added(categories)

    def __repr__(self):
        return ', '.join(list(sorted(self.added)))

    def __bool__(self):
        return bool(self.added)

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
        except Exception as ex:
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
