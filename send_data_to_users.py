#!.venv/bin/python
from datetime import date
from typing import Callable
import json

import sqlalchemy.orm.query

from loggers.loggers import log_info
from models.job import Job
from models.user import User
from models.telegram import bot_send_message
from models.database import DATABASE_NAME
from models.database import is_exist_db
from models.database import Session
from sqlalchemy.sql import and_


def format_data(job: Job) -> str:
    return f'{job.date_from} [{job.name}]({job.url}) {job.company} {job.place}'


def do_filter(query: sqlalchemy.orm.query.Query, subscribes: dict) -> dict:
    data = {'is_new_data': False}
    if subscribes:
        for key, value in subscribes.items():
            temp_query = query.filter(and_(Job.category == key, Job.id > value)).order_by(Job.id)
            data[key] = (temp_query.all())
            data['is_new_data'] = bool(data[key])
    return data


def main():
    data_to_send = dict()
    if not is_exist_db(DATABASE_NAME):
        log_info('База данных не найдена.\nПрограмма завершена.') 
        exit()
    with Session() as session:
        users = session.query(User).all()
        if users:
            for user in users:
                subscribes: dict = json.loads(user.subscribes)
                user_tg_id = user.user_tg_id

                query = session.query(Job)
                data: dict = do_filter(query, subscribes)

                if data['is_new_data']:
                    del data['is_new_data']
                    subscribes = {k: max(v, key=lambda i: i.id).id for k, v in data.items()}
                    raw_message_list = list()
                    [raw_message_list.extend(value) for value in data.values()]
                    formatted_message_list = map(format_data, raw_message_list)
                    log_info(f'Стартует рассылка пользователю {user_tg_id}...')
                    for message in formatted_message_list:
                        resp = bot_send_message(message, user_tg_id)
                        print(resp)
                    log_info(f'Рассылка пользователю {user_tg_id} завершена.')

                    user.subscribes = json.dumps(subscribes)
                else:
                    log_info(f'Новых данных для пользователя {user_tg_id} нет.')

            session.add_all(users)
            session.commit()


if __name__ == '__main__':
    main()
