"""Base class for all apps."""

import logging


class App:
    full_name = ''
    client_id = ''

    def __init__(self, config: dict):
        self.name = self.__name__
        self.log = logging.getLogger(self.name)
        self.config = config[self.name]
