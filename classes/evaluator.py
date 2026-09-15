from classes.logger import Logger


class Evaluator:
    def __init__(self, logger):
        if not isinstance(logger, Logger):
            raise ValueError("Evaluator logger must be a Logger")
        self.logger = logger

    def evaluate(self, question, context, response):
        self.logger.info("Evaluation request received")
        return None