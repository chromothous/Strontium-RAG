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
        self.history = []

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

    def add_user_message(self, query):
        self._validate_query(query)
        self.history.append({
            "role": "user",
            "content": query
        })
        self.logger.info("Conversation user message added to history")

    def add_assistant_message(self, response):
        if not isinstance(response, str):
            self.logger.error(
                "Conversation assistant response must be a string"
            )
            raise ValueError(
                "Conversation assistant response must be a string"
            )
        if not response.strip():
            self.logger.error(
                "Conversation assistant response cannot be empty"
            )
            raise ValueError(
                "Conversation assistant response cannot be empty"
            )
        self.history.append({
            "role": "assistant",
            "content": response
        })
        self.logger.info(
            "Conversation assistant message added to history"
        )

    def get_history(self):
        return [message.copy() for message in self.history]

    def validate_request(self, request):
        if not isinstance(request, dict):
            self.logger.error("Conversation request must be a dictionary")
            raise ValueError("Conversation request must be a dictionary")
        if "query" not in request:
            self.logger.error("Conversation request is missing query")
            raise ValueError("Conversation request is missing query")
        self._validate_query(request["query"])
        if "session_id" in request:
            session_id = request["session_id"]
            if not isinstance(session_id, str):
                self.logger.error(
                    "Conversation request session ID must be a string"
                )
                raise ValueError(
                    "Conversation request session ID must be a string"
                )
            if not session_id.strip():
                self.logger.error(
                    "Conversation request session ID cannot be empty"
                )
                raise ValueError(
                    "Conversation request session ID cannot be empty"
                )
        self.logger.info("Conversation request validated successfully")
        return request.copy()

    def validate_state(self, state):
        if not isinstance(state, dict):
            self.logger.error("Conversation state must be a dictionary")
            raise ValueError("Conversation state must be a dictionary")
        if "session_id" not in state:
            self.logger.error("Conversation state is missing session ID")
            raise ValueError("Conversation state is missing session ID")
        session_id = state["session_id"]
        if session_id is not None:
            if not isinstance(session_id, str):
                self.logger.error(
                    "Conversation state session ID must be a string"
                )
                raise ValueError(
                    "Conversation state session ID must be a string"
                )
            if not session_id.strip():
                self.logger.error(
                    "Conversation state session ID cannot be empty"
                )
                raise ValueError(
                    "Conversation state session ID cannot be empty"
                )
        self.logger.info("Conversation state validated successfully")
        return True

    def handle_failure(self, error, operation):
        if not isinstance(error, Exception):
            self.logger.error(
                "Conversation failure must be an Exception"
            )
            raise ValueError(
                "Conversation failure must be an Exception"
            )
        if not isinstance(operation, str):
            self.logger.error(
                "Conversation failure operation must be a string"
            )
            raise ValueError(
                "Conversation failure operation must be a string"
            )
        if not operation.strip():
            self.logger.error(
                "Conversation failure operation cannot be empty"
            )
            raise ValueError(
                "Conversation failure operation cannot be empty"
            )
        failure = {
            "success": False,
            "operation": operation,
            "error": str(error),
            "error_type": type(error).__name__
        }
        self.logger.error(
            f"Conversation operation failed: {operation}: {error}"
        )
        return failure

    def get_state(self):
        return self.state.copy()

    def request(self, query):
        self.logger.info("Conversation request received")
        return None