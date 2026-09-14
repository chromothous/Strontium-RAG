from classes.logger import Logger


class Conversation:
    def __init__(self, logger):
        if not isinstance(logger, Logger):
            raise ValueError("Conversation logger must be a Logger")
        self.logger = logger

    def request(self, query):
        self.logger.info("Conversation request received")
        return None