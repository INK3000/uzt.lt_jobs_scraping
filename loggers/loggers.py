import logging.config
from loggers.settings import logger_config

logging.config.dictConfig(logger_config)
# aliases for loggers
log_info = logging.getLogger('main_logger').info