from classes.logger import Logger


class Generator:
    def __init__(self, logger):
        if not isinstance(logger, Logger):
            raise ValueError("Generator logger must be a Logger")
        self.logger = logger

    def generate(self, query, context):
        self.logger.info("Generation request received")
        return None