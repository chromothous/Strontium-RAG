from classes.logger import Logger
from classes.context_builder import ContextBuilder
from classes.generator import Generator
from classes.citation import Citation


class Conversation:
    def __init__(self, logger, session_id=None):
        if not isinstance(logger, Logger):
            raise ValueError("Conversation logger must be a Logger")
        if session_id is not None:
            if not isinstance(session_id, str):
                raise ValueError("Conversation session ID must be a string")
            if not session_id.strip():
                raise ValueError("Conversation session ID cannot be empty")
        self.logger = logger
        self.session_id = session_id
        self.state = {
            "session_id": session_id
        }

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

    def build_context(self, query, results, context_builder):
        self._validate_query(query)
        if not isinstance(context_builder, ContextBuilder):
            self.logger.error(
                "Conversation context builder must be a ContextBuilder"
            )
            raise ValueError(
                "Conversation context builder must be a ContextBuilder"
            )
        context = context_builder.build(results)
        self.logger.info(
            "Conversation context constructed successfully"
        )
        return context

    def generate_response(self, query, context, generator, system_prompt):
        self._validate_query(query)
        if not isinstance(generator, Generator):
            self.logger.error(
                "Conversation generator must be a Generator"
            )
            raise ValueError(
                "Conversation generator must be a Generator"
            )
        response = generator.generate_with_provider(
            query,
            context,
            system_prompt
        )
        content = generator.handle_response(response)
        metadata = generator.get_generation_metadata(response)
        self.logger.info(
            "Conversation response generated successfully"
        )
        return {
            "response": content,
            "metadata": metadata
        }

    def add_citations(self, answer, results, citation):
        if not isinstance(answer, str):
            self.logger.error("Conversation answer must be a string")
            raise ValueError("Conversation answer must be a string")
        if not answer.strip():
            self.logger.error("Conversation answer cannot be empty")
            raise ValueError("Conversation answer cannot be empty")
        if not isinstance(results, (list, tuple)):
            self.logger.error("Conversation results must be a list or tuple")
            raise ValueError("Conversation results must be a list or tuple")
        if not isinstance(citation, Citation):
            self.logger.error(
                "Conversation citation component must be a Citation"
            )
            raise ValueError(
                "Conversation citation component must be a Citation"
            )
        context_items = citation.propagate_source_identity(
            results
        )
        citation_result = citation.cite_complete(
            answer,
            results
        )
        self.logger.info(
            f"Conversation citations integrated successfully: "
            f"{len(context_items)} sources"
        )
        return citation_result

    def get_state(self):
        return self.state.copy()

    def request(self, query):
        self.logger.info("Conversation request received")
        return None