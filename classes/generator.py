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

    def _build_prompt(self, query, context):
        return (
            "Context:\n"
            f"{context}\n\n"
            "Question:\n"
            f"{query}"
        )

    def build_prompt(self, query, context):
        self._validate_inputs(query, context)
        prompt = self._build_prompt(query, context)
        self.logger.info("Generation prompt constructed successfully")
        return prompt

    def generate(self, query, context):
        self._validate_inputs(query, context)
        self.logger.info("Generation request received")
        return None