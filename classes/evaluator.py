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

    def evaluate_retrieval(self, results, expected_sources):
        if not isinstance(results, (list, tuple)):
            self.logger.error("Evaluator retrieval results must be a list or tuple")
            raise ValueError("Evaluator retrieval results must be a list or tuple")
        if not isinstance(expected_sources, (list, tuple)):
            self.logger.error("Evaluator expected sources must be a list or tuple")
            raise ValueError("Evaluator expected sources must be a list or tuple")
        if not expected_sources:
            self.logger.error("Evaluator expected sources cannot be empty")
            raise ValueError("Evaluator expected sources cannot be empty")
        retrieved_sources = set()
        for result in results:
            if not isinstance(result, dict):
                self.logger.error("Evaluator retrieval result must be a dictionary")
                raise ValueError("Evaluator retrieval result must be a dictionary")
            if "chunk" not in result:
                self.logger.error("Evaluator retrieval result is missing chunk")
                raise ValueError("Evaluator retrieval result is missing chunk")
            chunk = result["chunk"]
            if not hasattr(chunk, "source"):
                self.logger.error("Evaluator retrieval chunk must contain source identity")
                raise ValueError("Evaluator retrieval chunk must contain source identity")
            retrieved_sources.add(chunk.source)
        expected = set()
        for source in expected_sources:
            if not isinstance(source, str):
                self.logger.error("Evaluator expected source must be a string")
                raise ValueError("Evaluator expected source must be a string")
            if not source.strip():
                self.logger.error("Evaluator expected source cannot be empty")
                raise ValueError("Evaluator expected source cannot be empty")
            expected.add(source)
        relevant_sources = retrieved_sources.intersection(expected)
        score = len(relevant_sources) / len(expected)
        self.logger.info(
            f"Retrieval evaluation completed: {len(relevant_sources)}/{len(expected)} relevant sources"
        )
        return {
            "score": score,
            "retrieved_sources": list(retrieved_sources),
            "expected_sources": list(expected),
            "relevant_sources": list(relevant_sources),
            "missing_sources": list(expected - retrieved_sources)
        }

    def evaluate(self, question, context, response):
        self.logger.info("Evaluation request received")
        return None