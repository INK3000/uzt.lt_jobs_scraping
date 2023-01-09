import sys

ARGV = sys.argv[1] if len(sys.argv) > 1 else ""
logger_config = {
    'version': 1,
    'formatters': {
        'blue': {
            'format': '\x1b[34;20m' + ARGV + ' {asctime} {levelname}: {message}' + '\x1b[0m',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'style': '{'
        },
        'yellow': {
            'format': '\x1b[33;20m' + ARGV + ' {asctime} {levelname}: {message}' + '\x1b[0m',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'style': '{'
        },
        'default': {
            'format': ARGV + ' {asctime} {levelname}: {message}',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'style': '{'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'blue'
        },
        'telegram': {
            'class': 'loggers.handlers.TelegramBotHandler',
            'level': 'INFO',
            'formatter': 'default'
        }
    },
    'loggers': {
        'main_logger': {
            'level': 'INFO',
            'handlers': ['console', 'telegram'],
            'propagate': False

        }
    },
    'disable_existing_loggers': False,
    # 'filters': {},
    # 'incremental': False,
    # 'root': {}, # '': {},
}
