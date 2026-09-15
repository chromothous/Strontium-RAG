from classes.logger import Logger


class Evaluator:
    def __init__(self, logger):
        if not isinstance(logger, Logger):
            raise ValueError("Evaluator logger must be a Logger")
        self.logger = logger

    def _validate_question(self, question):
        if not isinstance(question, str):
            self.logger.error("Evaluator question must be a string")
            raise ValueError("Evaluator question must be a string")
        if not question.strip():
            self.logger.error("Evaluator question cannot be empty")
            raise ValueError("Evaluator question cannot be empty")

    def _validate_context(self, context):
        if not isinstance(context, str):
            self.logger.error("Evaluator context must be a string")
            raise ValueError("Evaluator context must be a string")
        if not context.strip():
            self.logger.error("Evaluator context cannot be empty")
            raise ValueError("Evaluator context cannot be empty")

    def _validate_response(self, response):
        if not isinstance(response, str):
            self.logger.error("Evaluator response must be a string")
            raise ValueError("Evaluator response must be a string")
        if not response.strip():
            self.logger.error("Evaluator response cannot be empty")
            raise ValueError("Evaluator response cannot be empty")

    def _validate_expected_data(self, expected_data):
        if not isinstance(expected_data, dict):
            self.logger.error(
                "Evaluator expected data must be a dictionary"
            )
            raise ValueError(
                "Evaluator expected data must be a dictionary"
            )

    def validate_inputs(
        self,
        question,
        context,
        response,
        expected_data
    ):
        self._validate_question(question)
        self._validate_context(context)
        self._validate_response(response)
        self._validate_expected_data(expected_data)
        self.logger.info("Evaluation inputs validated successfully")
        return True

    def evaluate(self, question, context, response):
        self.logger.info("Evaluation request received")
        return None