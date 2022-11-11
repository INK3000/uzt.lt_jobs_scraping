#!/usr/bin/env python
from create_database import create_db
from bs4 import BeautifulSoup
from datetime import date
from loggers.loggers import log_info
from models.browser import Browser
from models.category import Category
from models.database import DATABASE_NAME
from models.database import is_exist_db
from models.database import Session
from models.job import Job
import re
from sqlalchemy import exc as sa_exc
import warnings


def filter_only_jobs_rows(tag: BeautifulSoup) -> bool:
    result = False
    if tag.name == 'tr':
        result = not tag.has_attr('class') or \
                 not re.compile('(TopGridPager|GridHeader|BottomGridPager)').search(''.join(tag.get('class')))
    return result


def save_to_file(text: str, filename: str) -> None:
    with open(filename, 'w') as file:
        file.write(text)


def get_event_target(href: str) -> str:
    pattern = re.compile(r"\('(.+)',")
    event_target = pattern.search(href).group(1)
    return event_target


def get_next_page_event_target(browser):
    try:
        next_btn = browser.soup.find(id=re.compile('NextBtn$'))
        href = next_btn.get('href')
        next_page_event_target = get_event_target(href)
    except AttributeError:
        next_page_event_target = None
    return next_page_event_target


def get_categories_list(browser: Browser) -> list:
    ul = browser.soup.find(id='ctl00_MainArea_UpdatePanel1').find_all('li')
    categories_list = list()
    for item in ul:
        a = item.find('a')
        # убираем количество вакансий и лишние пробелы
        name = re.compile('^[^(]+').search(a.text).group(0).strip()
        # href содержит ссылку типа
        # javascript:__doPostBack('ctl00$MainArea$GroupedPOSearchTab$ProffessionGroups$ctl03$ProfGroup','')
        # нам нужен только первый аргумент, который вернет функция get_event_target()
        href = a.get('href')
        event_target = get_event_target(href)
        categories_list.append(Category(name=name, event_target=event_target))
    return categories_list


def get_all_jobs_in_category(browser, category):
    jobs_list = list()
    event_target = category.event_target
    while event_target:
        browser.do_post_back(event_target, follow=True)
        table = browser.soup.find(id='ctl00_MainArea_SearchResultsList_POGrid')
        rows = table.find_all(filter_only_jobs_rows, recursive=False)
        for row in rows:
            date_from, date_to, job_name, company_name, company_place = row.find_all('td')
            full_job_url = browser.do_post_back(get_event_target(job_name.a.get('href')))
            # full_job_url содержит адрес страницы, itemID, а так же другие не важные параметры,
            # которые могут изменяться от сессии к сессии, но не влияют на конечный адрес страницы.
            # Однако они не позволяют обойти проверку на уникальность поля url при добавлении в базу.
            # Убираем лишние параметры из url, оставляем только адрес страницы и параметр itemID
            # результат сохраняем в short_job_url (постоянный и уникальный для каждой вакансии)
            r = re.compile(r'^(https:.+\?).+(itemID.+)$')
            s = r.search(full_job_url).groups()
            short_job_url = ''.join(s)
            jobs_list.append(Job(date_upd=date.today().isoformat(), category=category.id,
                                 company=company_name.text.strip(), date_from=date_from.text,
                                 date_to=date_to.text, name=job_name.text.strip(),
                                 url=short_job_url,
                                 place=company_place.text.strip()
                                 )
                             )
        event_target = get_next_page_event_target(browser)
    return jobs_list


def main():
    if not is_exist_db(DATABASE_NAME):
        create_db()

    start_url = 'https://uzt.lt/LDBPortal/Pages/ServicesForEmployees.aspx'
    with Browser(follow_redirects=True, verify=False, timeout=None) as browser:

        browser.go_url(url=start_url)
        if browser.response.is_success:
            log_info('Успешно перешли на стартовую страницу')
        else:
            log_info('Не удалось открыть стартовую страницу \n Работа программы завершена')
            exit()
        # получаем eventtarget для всех категорий
        # parsed_data будет содержать все собранные данные, ключи - eventtarget для каждой категории
        with Session() as session:
            # отключаем предупреждения от sqlalchemy, возникающие при появлении дублирующихся записей
            # хотя записи в таблицу не попадают, но предупреждения появляются и портят вывод в консоль
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=sa_exc.SAWarning)

                categories = session.query(Category).all()
                while not categories:
                    categories = get_categories_list(browser)
                    session.add_all(categories)
                    session.commit()

                for category in categories:
                    log_info(f'Начинаем собирать вакансии в категории {category.name} (id={category.id})...')

                    jobs_list = get_all_jobs_in_category(browser, category)
                    session.add_all(jobs_list)
                    session.commit()

                    log_info(f'В категории {category.name} собрано и сохранено {len(jobs_list)} вакансий.')
                    browser.go_url(url=start_url)

            log_info(f'Работа успешно завершена, все данные сохранены в файл {DATABASE_NAME}')


if __name__ == '__main__':
    main()
