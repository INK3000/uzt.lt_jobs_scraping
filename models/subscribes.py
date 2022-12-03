class Subscribes():
    '''
    class for users subscribes
    for init need subscribes
    '''

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
