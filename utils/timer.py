# main.py or timer.py
import time
import functools
import logging
from utils.logger import Logger

logger = Logger(logging.DEBUG)


def time_it(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time_ms = (end_time - start_time) * 1000  # Convert to milliseconds
        logger.timer(f"Function '{func.__name__}' executed in {elapsed_time_ms:.2f} ms")
        return result

    return wrapper
