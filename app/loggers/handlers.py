from logging import StreamHandler
from models import telegram


class TelegramBotHandler(StreamHandler):

    def emit(self, record):
        try:
            message = self.format(record)
            telegram.send_message(message)
        except RecursionError:
            raise
        except:
            self.handleError(record)
