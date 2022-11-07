from models.job import Job
from models.category import Category
from models.user import User
from models.database import create_db
import os


def create_database():
    create_db()


def is_created_db(database_name):
    return os.path.exists(database_name)
