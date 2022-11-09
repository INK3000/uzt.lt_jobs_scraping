#!/usr/bin/env python
from datetime import date
from loggers.loggers import log_info
from models.job import Job
from models.user import User
from models.telegram import bot_send_message
from models.database import DATABASE_NAME
from models.database import is_exist_db
from models.database import Session
from sqlalchemy.sql import and_


def get_users(session):
    return session.query(User).all()


def get_users_category(user) -> tuple:
    if len(user.category) > 0:
        return user.category.split(',')


def format_data(job: Job) -> str:
    return f'{job.date_from} [{job.name}]({job.url}) {job.company} {job.place}'


def main():
    data_to_send = dict()
    if not is_exist_db(DATABASE_NAME):
        exit()
    with Session() as session:
        users = get_users(session)
        if users:
            for user in users:
                category = get_users_category(user)
                today = date.today()
                if category:
                    message_list = map(format_data, session.query(Job).order_by(Job.date_from).filter(and_(Job.category.in_(category), Job.date_upd == today)).all())
                else:
                    message_list = map(format_data, session.query(Job).all())

                data_to_send[user.user_tg_id] = message_list

    for user_id, message_list in data_to_send.items():
        log_info(f'Стартует рассылка пользователю {user_id}...')
        for message in message_list:
            bot_send_message(message, user_id)
        log_info(f'рассылка пользователю {user_id} завершена.')




if __name__ == '__main__':
    main()
