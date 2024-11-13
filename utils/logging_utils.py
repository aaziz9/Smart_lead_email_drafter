import logging
from logging.handlers import RotatingFileHandler


LOG_FILE_PATH = "./logs/app_log.txt"


def get_logger():
    # Create a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Create a rotating file handler
    # file_handler = RotatingFileHandler(
    #     LOG_FILE_PATH,            # Log file name
    #     maxBytes=10 * 1024 * 1024,  # 10 MB max file size
    #     backupCount=5             # Keep 5 backup files
    # )

    # Set the log format
    formatter = logging.Formatter(
        "%(asctime)s - %(filename)s - %(levelname)s - %(message)s"
    )
    # file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Add the handler to the logger
    # logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger_instance = get_logger()
