import os
import logging
import time
from functools import wraps


class DecoLogger:
    def __init__(self, path):
        folder = path.rsplit(os.sep, 1)[0]
        os.makedirs(folder, exist_ok=True)
        self.app_logger = logging.getLogger("app")
        self.app_logger.setLevel(logging.INFO)
        self.app_handler = logging.FileHandler(path, mode="a")
        self.app_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        self.app_logger.addHandler(self.app_handler)

    def return_logging(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            self.app_logger.info(f"함수 '{func.__name__}' 리턴값: {result}")
            return result

        return wrapper

    def time_logging(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            self.app_logger.info(f"함수 '{func.__name__}' 실행시간: {execution_time}")
            return result

        return wrapper

    def error_logging(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)  # 함수 실행
            except Exception as e:
                result = str(e)
            self.app_logger.info(f"함수 '{func.__name__}' 리턴값: {result}")
            return result

        return wrapper
