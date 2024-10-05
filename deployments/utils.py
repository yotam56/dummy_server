from PIL import Image
import base64
from io import BytesIO
import logging
import time
from colorlog import ColoredFormatter
import functools


class SingletonMeta(type):
    """A metaclass for the Singleton pattern."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Logger(metaclass=SingletonMeta):
    def __init__(self, level=logging.INFO):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level)

        # Check if the logger already has handlers to avoid duplicate logs
        if not self.logger.hasHandlers():
            handler = logging.StreamHandler()

            # Color formatting
            log_colors = {
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
                "TIMER": "blue",
            }

            formatter = ColoredFormatter(
                "%(log_color)s%(levelname)-8s%(reset)s %(message)s [%(module)s/%(funcName)s/line %(lineno)d]",
                datefmt=None,
                reset=True,
                log_colors=log_colors,
            )

            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        logging.addLevelName(25, "TIMER")

    def get_logger(self):
        return self.logger

    def timer(self, message, *args, **kwargs):
        if self.logger.isEnabledFor(25):
            self.logger._log(25, message, args, **kwargs)


logger = Logger(logging.DEBUG).get_logger()


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

def decode_base64_to_image(image_base64: str) -> Image.Image:
    try:
        image_data = base64.b64decode(image_base64)
        image = Image.open(BytesIO(image_data)).convert('RGB')
        logger.info("Image decoded successfully")
        return image
    except Exception as e:
        logger.error(f"Error decoding base64 image: {str(e)}")
        raise