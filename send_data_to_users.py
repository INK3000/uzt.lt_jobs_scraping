#!/usr/bin/env python
import datetime
from datetime import date
from typing import Callable

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


def int_from_isodate(isodate: str) -> int:
    result = 0
    if isodate:
        result = int(''.join(isodate.split('-')))
    return result


def fltr_date_less_eq_than(isodate: str) -> Callable:
    isodate = int_from_isodate(isodate)

    def wrap(job: Job) -> bool:
        isodate_from_bd = int_from_isodate(job.date_upd)
        return isodate <= isodate_from_bd

    return wrap


def main():
    data_to_send = dict()
    if not is_exist_db(DATABASE_NAME):
        exit()
    with Session() as session:
        users = get_users(session)
        if users:
            for user in users:
                category = get_users_category(user)
                today = date.today().isoformat()
                if category:
                    jobs_list = session.query(Job).order_by(Job.date_from).filter(Job.category.in_(category)).all()
                else:
                    jobs_list = session.query(Job).all()

                filter_fn = fltr_date_less_eq_than(user.last_send_date)
                jobs_list = list(filter(filter_fn, jobs_list))

                if jobs_list:
                    message_list = map(format_data, jobs_list)
                    data_to_send[user] = message_list
            try:
                for user, message_list in data_to_send.items():
                    user_tg_id = user.user_tg_id
                    log_info(f'Стартует рассылка пользователю {user_tg_id}...')
                    for message in message_list:
                        bot_send_message(message, user_tg_id)
                    log_info(f'рассылка пользователю {user_tg_id} завершена.')
                    user.last_send_date = today
            except Exception as e:
                log_info(e)

            session.add_all(users)
            session.commit()


if __name__ == '__main__':
    main()
