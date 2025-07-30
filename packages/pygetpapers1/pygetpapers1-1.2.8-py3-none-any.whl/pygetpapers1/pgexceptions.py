import logging


class pygetpapers1Error(Exception):
    """This error is raised from classes in pygetpapers1 package.
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        logging.warning(self.message)
