import logging

class Logger:
    def __init__(self, name: str = "data_lib"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            formatter = logging.Formatter("[%(levelname)s] %(asctime)s - %(message)s")
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def info(self, message: str):
        self.logger.info(message)

    def error(self, message: str):
        self.logger.error(message)

    def debug(self, message: str):
        self.logger.debug(message)
