import re
import urllib

import httpx
from bs4 import BeautifulSoup


class Browser(httpx.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._headers = self.load_headers(filename="headers")
        self.payload = None
        self.soup = None
        self.action_url = None
        self.response = None
        self.cookies = None
        self.data = dict()

    def get_soup(self, response=None) -> BeautifulSoup:
        return BeautifulSoup(response or self.response.text, "lxml")

    def go_url(self, url: str) -> None:
        """
        выполняет GET запрос на указанный url, при этом собирает куки и необходимые скрытые поля
        для последующий POST запросов
        :param url:
        :return:
        """
        tries = 5
        while True:
            self.response = self.get(url=url)
            if not self.cookies:
                self.cookies = self.response.cookies
            if not self.headers.get("Cookie"):
                self.headers["Cookie"] = "; ".join(
                    [f"{key}={self.cookies[key]}" for key in self.cookies]
                )
            self.soup = self.get_soup()
            self.base_url = re.compile(r"^.+/").search(url).group(0)
            try:
                self.action_url = self.soup.find(id="aspnetForm").get("action")
            except AttributeError:
                if tries == 0:
                    print(
                        f"Не удается открыть страницу {url} \n Работа программы завершена."
                    )
                    exit()
                else:
                    tries -= 1
            else:
                break
        self.payload = {
            "ctl00$MasterScriptManager": "ctl00$MainArea$UpdatePanel1|",
            "ctl00$calendarLayoutHelperText": "",
            "ctl00$MainArea$QuickSearchByLocalityControl$Keyword": "",
            "ctl00$MainArea$QuickSearchByLocalityControl$poPlaces": "-1",
            "ctl00$MainArea$QuickSearchByLocalityControl$LocalityRegisteredOnly": "on",
            "ctl00$MainArea$QuickSearchByLocalityControl$PeriodPicker": "6",
            "__ASYNCPOST": "true",
            "__LASTFOCUS": "",
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": self.soup.find(id="__VIEWSTATE").get("value"),
            "__VIEWSTATEGENERATOR": self.soup.find(id="__VIEWSTATEGENERATOR").get(
                "value"
            ),
            "__EVENTVALIDATION": self.soup.find(id="__EVENTVALIDATION").get("value"),
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
        self.payload[
            "ctl00$MasterScriptManager"
        ] = f"ctl00$MainArea$UpdatePanel1| {event_target}"
        self.payload["__EVENTTARGET"] = event_target
        response = self.post(url=self.action_url, data=self.payload)
        # self.soup = self.get_soup()
        if "pageRedirect" in response.text:
            splitted_text = response.text.split("|")
            redirect_url = urllib.parse.unquote(f"https://uzt.lt{splitted_text[-2]}")
            if follow:
                self.go_url(redirect_url)
        else:
            self.payload["__VIEWSTATE"] = (
                re.compile(r"__VIEWSTATE\|([^|]+)").search(response.text).group(1)
            )
            self.payload["__EVENTVALIDATION"] = (
                re.compile(r"__EVENTVALIDATION\|([^|]+)").search(response.text).group(1)
            )
            self.soup = self.get_soup(response.text)

        return redirect_url

    @staticmethod
    def load_headers(filename: str) -> dict:
        with open(filename, "r") as file:
            pattern = re.compile(r"^(.*): (.*)")
            headers = dict()
            for line in file:
                m = re.match(pattern, line)
                if len(m.groups()) == 2:
                    key, value = m.groups()
                    headers[key] = value
        return headers
