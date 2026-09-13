from classes.logger import Logger
from classes.context_builder import ContextBuilder
from classes.llm_provider import LLMProvider


class Generator:
    def __init__(self, logger, provider=None):
        if not isinstance(logger, Logger):
            raise ValueError("Generator logger must be a Logger")
        if provider is not None and not isinstance(provider, LLMProvider):
            raise ValueError("Generator provider must be an LLMProvider")
        self.logger = logger
        self.provider = provider

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

    def _validate_context_available(self, context):
        if not isinstance(context, str):
            self.logger.error("Generator context must be a string")
            raise ValueError("Generator context must be a string")
        if not context.strip():
            self.logger.error(
                "Generator cannot generate without usable context"
            )
            raise ValueError(
                "Generator cannot generate without usable context"
            )

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

    def build_messages(self, query, context, system_prompt):
        if not isinstance(system_prompt, str):
            self.logger.error("Generator system prompt must be a string")
            raise ValueError("Generator system prompt must be a string")
        if not system_prompt.strip():
            self.logger.error("Generator system prompt cannot be empty")
            raise ValueError("Generator system prompt cannot be empty")
        self._validate_inputs(query, context)
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": (
                    "Context:\n"
                    f"{context}\n\n"
                    "Question:\n"
                    f"{query}"
                )
            }
        ]
        self.logger.info("System and user prompts separated successfully")
        return messages

    def generate(self, query, context):
        self._validate_inputs(query, context)
        self.logger.info("Generation request received")
        return None

    def generate_with_provider(self, query, context, system_prompt):
        if self.provider is None:
            self.logger.error("Generator provider is not configured")
            raise ValueError("Generator provider is not configured")
        self._validate_context_available(context)
        messages = self.build_messages(
            query,
            context,
            system_prompt
        )
        response = self.provider.generate(messages)
        self.logger.info("Generation request sent to LLM provider")
        return response

    def _extract_response(self, response):
        if isinstance(response, str):
            if not response.strip():
                self.logger.error("Generator provider returned an empty response")
                raise ValueError("Generator provider returned an empty response")
            return response
        if isinstance(response, dict):
            if "response" not in response:
                self.logger.error(
                    "Generator provider response is missing response content"
                )
                raise ValueError(
                    "Generator provider response is missing response content"
                )
            content = response["response"]
            if not isinstance(content, str):
                self.logger.error(
                    "Generator provider response content must be a string"
                )
                raise ValueError(
                    "Generator provider response content must be a string"
                )
            if not content.strip():
                self.logger.error(
                    "Generator provider returned empty response content"
                )
                raise ValueError(
                    "Generator provider returned empty response content"
                )
            return content
        self.logger.error(
            "Generator provider response has an invalid structure"
        )
        raise ValueError(
            "Generator provider response has an invalid structure"
        )

    def handle_response(self, response):
        content = self._extract_response(response)
        self.logger.info("Generation response handled successfully")
        return content