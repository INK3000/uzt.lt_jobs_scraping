#!.venv/bin/python
import json
from typing import Sized

import sqlalchemy.orm.query
from sqlalchemy.sql import and_

from create_database import create_database
from loggers.loggers import log_info
from models import telegram
from models.category import Category
from models.database import Session
from models.job import Job
from models.user import User


def format_data(job: Job) -> str:
    return f"{job.date_from} [{job.name}]({job.url}) {job.company} {job.place}"


def do_filter(query: sqlalchemy.orm.query.Query, subscribes: dict) -> dict:
    data = {"is_new_data": False}
    if subscribes:
        for key, value in subscribes.items():
            if not value:
                value = 0
            temp_query = query.filter(
                and_(Job.category == key, Job.id > value)
            ).order_by(Job.id)
            data[key] = temp_query.all()
            data["is_new_data"] = bool(data[key])
    return data


def do_merge(
    messages: Sized,
    part_size: int = 30,
    header: str = "",
):
    start = 0
    # end = 0
    while start <= len(messages):
        # end += part_size
        chunk = "\n\n".join([format_data(i) for i in messages[start:part_size]])
        result = f"*{header}* \n\n{chunk}\n\n"
        yield result
        start += part_size
        header = ""


def main():

    with Session() as session:
        users = session.query(User).all()
        categories = session.query(Category).order_by(Category.id).all()
        if not users:
            log_info("Нет пользователей с активной подпиской.")
            return
        for user in users:
            subscribes: dict = json.loads(user.subscribes)
            user_tg_id = user.user_tg_id

            query = session.query(Job)
            data: dict = do_filter(query, subscribes)

            if data["is_new_data"]:
                del data["is_new_data"]
                log_info(f"Стартует рассылка пользователю {user_tg_id}...")
                for category, jobs_list in data.items():
                    if jobs_list:
                        category_name = categories[int(category) - 1].name
                        info_message = (
                            f"В категории {category_name} {len(jobs_list)} вакансий."
                        )
                        log_info(info_message)
                        subscribes[category] = max(jobs_list, key=lambda i: i.id).id
                        formatted_message_list = do_merge(
                            jobs_list, header=info_message
                        )
                        for message in formatted_message_list:
                            resp = telegram.send_message(message, user_tg_id)

                log_info(f"Рассылка пользователю {user_tg_id} завершена.")
                user.subscribes = json.dumps(subscribes)
            else:
                log_info(f"Новых данных для пользователя {user_tg_id} нет.")

        session.add_all(users)
        session.commit()


if __name__ == "__main__":
    create_database()
    main()
