from bs4 import BeautifulSoup
from dataclasses import dataclass, field
import httpx
import logging.config
import re
from settings import logger_config
import urllib


logging.config.dictConfig(logger_config)
# aliases for loggers
_debug = logging.getLogger('main_logger').debug
_info = logging.getLogger('main_logger').info


@dataclass
class Category:
    name: str
    event_target: str
    jobs_list: list = field(default_factory=list)


@dataclass
class Job:
    category: str
    company: str
    date_from: str
    date_to: str
    name: str
    place: str
    url: str


class Browser(httpx.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._headers = load_headers(filename='headers')
        self.payload = None
        self.soup = None
        self.action_url = None
        self.response = None
        self.cookies = None
        self.data = dict()

    def get_soup(self, response=None) -> BeautifulSoup:
        return BeautifulSoup(response or self.response.text, 'lxml')

    def go_url(self, url: str, event_target: str = '') -> None:
        self.response = self.get(url=url)
        if not self.cookies:
            self.cookies = self.response.cookies
        if not self.headers.get('Cookie'):
            self.headers['Cookie'] = '; '.join([f'{key}={self.cookies[key]}' for key in self.cookies])
        self.soup = self.get_soup()
        self.base_url = re.compile(r'^.+/').search(url).group(0)
        self.action_url = self.soup.find(id='aspnetForm').get('action')
        self.payload = {
                "ctl00$MasterScriptManager": f"ctl00$MainArea$UpdatePanel1| {event_target}",
                "ctl00$calendarLayoutHelperText": "",
                "ctl00$MainArea$QuickSearchByLocalityControl$Keyword": "",
                "ctl00$MainArea$QuickSearchByLocalityControl$poPlaces": "-1",
                "ctl00$MainArea$QuickSearchByLocalityControl$LocalityRegisteredOnly": "on",
                "ctl00$MainArea$QuickSearchByLocalityControl$PeriodPicker": "6",
                "__ASYNCPOST": "true",
                "__LASTFOCUS": "",
                "__EVENTTARGET": event_target,
                "__EVENTARGUMENT": "",
                '__VIEWSTATE': self.soup.find(id='__VIEWSTATE').get('value'),
                '__VIEWSTATEGENERATOR': self.soup.find(id='__VIEWSTATEGENERATOR').get('value'),
                '__EVENTVALIDATION': self.soup.find(id='__EVENTVALIDATION').get('value'),
        }

    def do_post_back(self, event_target: str, follow: bool = False) -> str:
        """
        выполняет POST запрос, получает redirect_url и перенаправляет browser на этот url.
        так же возвращает redirect_url
        :param follow: если True браузера перейдет на redirect_url, иначе только вернет redirect_url
        :param event_target: строка типа 'ctl00_MainArea_UpdatePanel1' берется из аттрибута href
        :return: redirect_url, по которому откроется страница, связанная с event_target
        """
        redirect_url = self.action_url
        self.payload['ctl00$MasterScriptManager'] = f"ctl00$MainArea$UpdatePanel1| {event_target}"
        self.payload['__EVENTTARGET'] = event_target
        response = self.post(url=self.action_url, data=self.payload)
        # self.soup = self.get_soup()
        if 'pageRedirect' in response.text:
            splitted_text = response.text.split('|')
            redirect_url = urllib.parse.unquote(f'https://uzt.lt{splitted_text[-2]}')
            if follow:
                self.go_url(redirect_url)
        else:
            self.payload['__VIEWSTATE'] = re.compile(r'__VIEWSTATE\|([^|]+)').search(response.text).group(1)
            self.payload['__EVENTVALIDATION'] = re.compile(r'__EVENTVALIDATION\|([^|]+)').search(response.text).group(1)
            self.soup = self.get_soup(response)
        return redirect_url


def load_headers(filename: str) -> dict:
    with open(filename, 'r') as file:
        pattern = re.compile(r'^(.*): (.*)')
        headers = dict()
        for line in file:
            m = re.match(pattern, line)
            if len(m.groups()) == 2:
                key, value = m.groups()
                headers[key] = value
    return headers


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


def get_next_page_event_target(browser):
    try:
        next_btn = browser.soup.find(id=re.compile('NextBtn$'))
        href = next_btn.get('href')
        next_page_event_target = get_event_target(href)
    except AttributeError as e:
        next_page_event_target = None
    return next_page_event_target


def get_all_jobs_in_category(browser, category):
    event_target = category.event_target
    while event_target:
        browser.do_post_back(event_target, follow=True)
        table = browser.soup.find(id='ctl00_MainArea_SearchResultsList_POGrid')
        rows = table.find_all(filter_only_jobs_rows, recursive=False)
        for row in rows:
            date_from, date_to, job_name, company_name, company_place = row.find_all('td')
            category.jobs_list.append(Job(category=category.name,
                                          company=company_name.text.strip(), date_from=date_from.text,
                                          date_to=date_to.text, name=job_name.text.strip(),
                                          url=browser.do_post_back(get_event_target(job_name.a.get('href'))),
                                          place=company_place.text.strip()
                                          )
                                      )
        event_target = get_next_page_event_target(browser)
    _info(f'В категории {category.name} собрано {len(category.jobs_list)} вакансий.')
    return category.jobs_list


def main():
    start_url = 'https://www.uzt.lt/LDBPortal/Pages/ServicesForEmployees.aspx'
    with Browser(follow_redirects=True, verify=False) as browser:

        browser.go_url(url=start_url)
        if browser.response.is_success:
            _info('Успешно перешли на стартовую страницу')
        else:
            _info('Не удалось открыть стартовую страницу')
        # получаем eventtarget для всех категорий
        # parsed_data будет содержать все собранные данные, ключи - eventtarget для каждой категории
        parsed_data = get_categories_list(browser)
        for category in parsed_data:
            _info(f'Начинаем собирать вакансии в категории {category.name}...')
            get_all_jobs_in_category(browser, category)
            browser.go_url(url=start_url)


if __name__ == '__main__':
    main()
