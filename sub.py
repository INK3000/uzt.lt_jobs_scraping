
from models.database import Session
from models.category import Category
from models.user import User


class Subscribes():
    def __init__ (self, subscribes_d, categories):
        self.added  = subscribes_d
        self.not_added = self.get_not_added(categories)

    
    def get_not_added(self, categories):
        all = {str(category.id): category.last_id for category in categories}
        result = {key: val for key, val in all.items() if key not in self.added}
        return result


    def update(self, input, oper):
        to_add_list = self.text_to_list(input)
         
        pass


    def remove(self, input):
        to_add_list = self.text_to_list(input)
        pass


    @staticmethod
    def text_to_list(text):
        result_list = [i.strip() for i in text.split(',')]
        return result_list


def main():
    with Session() as session:
        categories = session.query(Category).all()
        user = session.query(User).filter(User.id == 1).one_or_none()
        subscribes = Subscribes(user.subscribes, categories)
        print(subscribes.not_added)
        


if __name__ == '__main__':
    main()
