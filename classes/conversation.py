from classes.logger import Logger


class Conversation:
    def __init__(self, logger):
        if not isinstance(logger, Logger):
            raise ValueError("Conversation logger must be a Logger")
        self.logger = logger

    def _validate_query(self, query):
        if not isinstance(query, str):
            self.logger.error("Conversation query must be a string")
            raise ValueError("Conversation query must be a string")
        if not query.strip():
            self.logger.error("Conversation query cannot be empty")
            raise ValueError("Conversation query cannot be empty")

    def handle_query(self, query):
        self._validate_query(query)
        self.logger.info("Conversation query validated successfully")
        return query

    def request(self, query):
        self.logger.info("Conversation request received")
        return None