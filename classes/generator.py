from classes.logger import Logger
from classes.context_builder import ContextBuilder


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

    def build_context_prompt(self, query, results, context_builder):
        if not isinstance(context_builder, ContextBuilder):
            self.logger.error(
                "Generator context builder must be a ContextBuilder"
            )
            raise ValueError(
                "Generator context builder must be a ContextBuilder"
            )
        context = context_builder.build(results)
        prompt = self.build_prompt(query, context)
        self.logger.info(
            "Generation prompt constructed from retrieved context"
        )
        return prompt

    def generate(self, query, context):
        self._validate_inputs(query, context)
        self.logger.info("Generation request received")
        return None