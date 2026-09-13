from classes.logger import Logger


class Generator:
    def __init__(self, logger):
        if not isinstance(logger, Logger):
            raise ValueError("Generator logger must be a Logger")
        self.logger = logger

    def _validate_inputs(self, query, context):
        if not isinstance(query, str):
            self.logger.error("Generator query must be a string")
            raise ValueError("Generator query must be a string")
        if not query.strip():
            self.logger.error("Generator query cannot be empty")
            raise ValueError("Generator query cannot be empty")
        if not isinstance(context, str):
            self.logger.error("Generator context must be a string")
            raise ValueError("Generator context must be a string")
        if not context.strip():
            self.logger.error("Generator context cannot be empty")
            raise ValueError("Generator context cannot be empty")

    def generate(self, query, context):
        self._validate_inputs(query, context)
        self.logger.info("Generation inputs validated successfully")
        return None