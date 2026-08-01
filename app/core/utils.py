import logging


class LoggingMessage:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.handler = logging.StreamHandler()
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.INFO)


log = LoggingMessage()
