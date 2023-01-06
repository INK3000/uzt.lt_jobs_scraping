import httpx

from settings import ADMIN_TELEGRAM_USER_ID, BOT_TOKEN

URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_message(message, chat_id=ADMIN_TELEGRAM_USER_ID):
    url = f"{URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "markdown"}
    resp = httpx.post(url=url, data=payload)
    return resp
