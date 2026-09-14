from classes.logger import Logger
from classes.context_builder import ContextBuilder


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

    def get_state(self):
        return self.state.copy()

    def request(self, query):
        self.logger.info("Conversation request received")
        return None