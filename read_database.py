from models.category import Category
from models.job import Job
from models.database import DATABASE_NAME
from models.database import is_exist_db
from models.database import Session


def main():
    if not is_exist_db(DATABASE_NAME):
        exit()
    with Session() as session:
        it = session.query(Job, Category).join(Category).all()
        [print(row.Job.name, row.Category.name) for row in it]

    pass


if __name__ == '__main__':
    main()