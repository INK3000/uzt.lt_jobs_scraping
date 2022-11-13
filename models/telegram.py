import httpx
import os

ADMIN_TELEGRAM_USER_ID = os.environ.get('ADMIN_TELEGRAM_USER_ID')
BOT_TOKEN = os.getenv('BOT_TOKEN')
URL = f'https://api.telegram.org/bot{BOT_TOKEN}'


def bot_get_message():
    url = f'{URL}/getUpdates'
    resp = httpx.get(url=url)
    data = resp.json()
    return data.get('result')


def bot_send_message(message, chat_id=ADMIN_TELEGRAM_USER_ID):
    url = f'{URL}/sendMessage'
    payload = {'chat_id': chat_id,
               'text': message,
               'parse_mode': 'markdown'}
    resp = httpx.post(url=url, data=payload)
    return resp

