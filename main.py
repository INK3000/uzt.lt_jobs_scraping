#!.venv/bin/python
import re
import time
from multiprocessing import Pool

from bs4 import BeautifulSoup
from sqlalchemy import func

from create_database import create_database
from loggers.loggers import log_info
from models.browser import Browser
from models.category import Category
from models.database import Session
from models.job import Job

START_URL = "https://portal.uzt.lt/LDBPortal/Pages/ServicesForEmployees.aspx"


def filter_only_jobs_rows(tag: BeautifulSoup) -> bool:
    result = False
    if tag.name == "tr":
        result = not tag.has_attr("class") or not re.compile(
            "(TopGridPager|GridHeader|BottomGridPager)"
        ).search("".join(tag.get("class")))
    return result


def save_to_file(text: str, filename: str) -> None:
    with open(filename, "w") as file:
        file.write(text)


def get_event_target(href: str) -> str:
    pattern = re.compile(r"\('(.+)',")
    event_target = pattern.search(href).group(1)
    return event_target


def get_next_page_event_target(browser):
    try:
        next_btn = browser.soup.find(id=re.compile("NextBtn$"))
        href = next_btn.get("href")
        next_page_event_target = get_event_target(href)
    except AttributeError:
        next_page_event_target = None
    return next_page_event_target


def get_categories_list(browser: Browser) -> list:
    ul = browser.soup.find(id="ctl00_MainArea_UpdatePanel1").find_all("li")
    categories_list = list()
    for item in ul:
        a = item.find("a")
        # убираем количество вакансий и лишние пробелы
        name = re.compile("^[^(]+").search(a.text).group(0).strip()
        # href содержит ссылку типа
        # javascript:__doPostBack('ctl00$MainArea$GroupedPOSearchTab$ProffessionGroups$ctl03$ProfGroup','')
        # нам нужен только первый аргумент, который вернет функция get_event_target()
        href = a.get("href")
        event_target = get_event_target(href)
        categories_list.append(Category(name=name, event_target=event_target))
    return categories_list


def get_all_jobs_in_category(browser, category):
    jobs_list = list()
    event_target = category.event_target
    while event_target:
        browser.do_post_back(event_target, follow=True)
        table = browser.soup.find(id="ctl00_MainArea_SearchResultsList_POGrid")
        rows = table.find_all(filter_only_jobs_rows, recursive=False)
        for row in rows:
            try:
                (
                    date_from,
                    date_to,
                    job_name,
                    company_name,
                    company_place,
                ) = row.find_all("td")
                full_job_url = browser.do_post_back(
                    get_event_target(job_name.a.get("href"))
                )
                # full_job_url содержит адрес страницы, itemID, а так же другие не важные параметры,
                # которые могут изменяться от сессии к сессии, но не влияют на конечный адрес страницы.
                # Однако они не позволяют обойти проверку на уникальность поля url при добавлении в базу.
                # Убираем лишние параметры из url, оставляем только адрес страницы и параметр itemID
                # результат сохраняем в short_job_url (постоянный и уникальный для каждой вакансии)
                r = re.compile(r"^(https:.+\?).+(itemID.+)$")
                s = r.search(full_job_url).groups()
                short_job_url = "".join(s)
                jobs_list.append(
                    Job(
                        date_upd=time.time(),
                        category=category.id,
                        company=company_name.text.strip(),
                        date_from=date_from.text,
                        date_to=date_to.text,
                        name=job_name.text.strip(),
                        url=short_job_url,
                        place=company_place.text.strip(),
                    )
                )
            except AttributeError as e:
                log_info(
                    f"Возникла ошибка при работе с категорией {category.name} (id={category.id}).\n"
                    f"Описание ошибки:\n{e}\n"
                    f"Продолжаем работу."
                )
                continue
        event_target = get_next_page_event_target(browser)
    return jobs_list


def process_get_jobs_in_category(category: Category) -> None:

    browser = Browser(follow_redirects=True, verify=False, timeout=None)
    session = Session()

    # инициализируем браузер стартовой страницей
    browser.go_url(url=START_URL)

    try:
        log_info(
            f"Начинаем собирать вакансии в категории {category.name} (id={category.id})..."
        )
        # создаем список из объектов Job для определенной категории,
        # затем реверсируем, чтобы верхние записи на странице имели более свежий индекс в базе
        # сохраняем в базу список
        jobs_list_from_site = set(get_all_jobs_in_category(browser, category))
        jobs_list_from_base = set(
            session.query(Job).filter(Job.category == category.id).all()
        )
        new_jobs_list = list(jobs_list_from_site.difference(jobs_list_from_base))
        new_jobs_list = sorted(new_jobs_list, key=lambda i: i.date_upd, reverse=True)

        session.add_all(new_jobs_list)
        session.commit()

        # получаем id верхней вакансии и сохраняем его в поле last_id для текущей категории
        category.last_id = (
            session.query(func.max(Job.id)).filter(Job.category == category.id).one()[0]
        )
        session.add(category)
        session.commit()

        log_info(
            f"В категории {category.name} (id={category.id}) собрано и сохранено {len(new_jobs_list)} вакансий."
        )

    except Exception as e:
        log_info(
            f"Возникла ошибка при работе с категорией {category.name} (id={category.id}).\n"
            f"Описание ошибки:\n{e}\n"
            f"Продолжаем работу."
        )
    finally:
        session.close()
        log_info(f"Сессия закрыта (id={category.id})")
        browser.close()
        log_info(f"Браузер закрыт (id={category.id})")


def main():
    create_database()
    with Session() as session:
        # создаем список из объектов Category
        categories = session.query(Category).all()
        while not categories:
            with Browser(follow_redirects=True, verify=False, timeout=None) as browser:
                # инициализируем браузер стартовой страницей
                browser.go_url(url=START_URL)
                categories = get_categories_list(browser)
                session.add_all(categories)
                session.commit()

    with Pool(10) as p:
        p.map(process_get_jobs_in_category, categories)
    log_info("Работа успешно завершена, все данные сохранены")


if __name__ == "__main__":
    main()
