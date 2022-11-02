logger_config = {
    'version': 1,
    'formatters': {
        'std_format': {
            'format': '{asctime} {levelname}: {message}',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'style': '{'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'std_format'
        }
    },
    'loggers': {
        'main_logger': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False

        }
    },
    'disable_existing_loggers': False,
    # 'filters': {},
    # 'incremental': False,
    # 'root': {}, # '': {},
}

