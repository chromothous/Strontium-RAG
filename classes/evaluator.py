import re
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

    def _get_content_terms(self, text):
        stopwords = {
            "a",
            "an",
            "and",
            "are",
            "as",
            "at",
            "be",
            "by",
            "for",
            "from",
            "in",
            "is",
            "it",
            "of",
            "on",
            "or",
            "that",
            "the",
            "this",
            "to",
            "was",
            "were",
            "with"
        }
        terms = set(
            re.findall(r"\b\w+\b", text.lower())
        )
        return terms - stopwords

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
            self.logger.error(
                "Evaluator retrieval results must be a list or tuple"
            )
            raise ValueError(
                "Evaluator retrieval results must be a list or tuple"
            )
        if not isinstance(expected_sources, (list, tuple)):
            self.logger.error(
                "Evaluator expected sources must be a list or tuple"
            )
            raise ValueError(
                "Evaluator expected sources must be a list or tuple"
            )
        if not expected_sources:
            self.logger.error(
                "Evaluator expected sources cannot be empty"
            )
            raise ValueError(
                "Evaluator expected sources cannot be empty"
            )
        retrieved_sources = set()
        for result in results:
            if not isinstance(result, dict):
                self.logger.error(
                    "Evaluator retrieval result must be a dictionary"
                )
                raise ValueError(
                    "Evaluator retrieval result must be a dictionary"
                )
            if "chunk" not in result:
                self.logger.error(
                    "Evaluator retrieval result is missing chunk"
                )
                raise ValueError(
                    "Evaluator retrieval result is missing chunk"
                )
            chunk = result["chunk"]
            if not hasattr(chunk, "source"):
                self.logger.error(
                    "Evaluator retrieval chunk must contain source identity"
                )
                raise ValueError(
                    "Evaluator retrieval chunk must contain source identity"
                )
            retrieved_sources.add(chunk.source)
        expected = set()
        for source in expected_sources:
            if not isinstance(source, str):
                self.logger.error(
                    "Evaluator expected source must be a string"
                )
                raise ValueError(
                    "Evaluator expected source must be a string"
                )
            if not source.strip():
                self.logger.error(
                    "Evaluator expected source cannot be empty"
                )
                raise ValueError(
                    "Evaluator expected source cannot be empty"
                )
            expected.add(source)
        relevant_sources = retrieved_sources.intersection(expected)
        score = len(relevant_sources) / len(expected)
        self.logger.info(
            f"Retrieval evaluation completed: "
            f"{len(relevant_sources)}/{len(expected)} relevant sources"
        )
        return {
            "score": score,
            "retrieved_sources": list(retrieved_sources),
            "expected_sources": list(expected),
            "relevant_sources": list(relevant_sources),
            "missing_sources": list(expected - retrieved_sources)
        }

    def evaluate_context(self, context, expected_content):
        self._validate_context(context)
        if not isinstance(expected_content, (list, tuple)):
            self.logger.error(
                "Evaluator expected content must be a list or tuple"
            )
            raise ValueError(
                "Evaluator expected content must be a list or tuple"
            )
        if not expected_content:
            self.logger.error(
                "Evaluator expected content cannot be empty"
            )
            raise ValueError(
                "Evaluator expected content cannot be empty"
            )
        expected = []
        for content in expected_content:
            if not isinstance(content, str):
                self.logger.error(
                    "Evaluator expected context content must be a string"
                )
                raise ValueError(
                    "Evaluator expected context content must be a string"
                )
            if not content.strip():
                self.logger.error(
                    "Evaluator expected context content cannot be empty"
                )
                raise ValueError(
                    "Evaluator expected context content cannot be empty"
                )
            expected.append(content)
        present = [
            content
            for content in expected
            if content in context
        ]
        missing = [
            content
            for content in expected
            if content not in context
        ]
        score = len(present) / len(expected)
        self.logger.info(
            f"Context evaluation completed: "
            f"{len(present)}/{len(expected)} expected items present"
        )
        return {
            "score": score,
            "expected_content": expected,
            "present_content": present,
            "missing_content": missing
        }

    def evaluate_generation(self, response, expected_answer):
        self._validate_response(response)
        if not isinstance(expected_answer, str):
            self.logger.error(
                "Evaluator expected answer must be a string"
            )
            raise ValueError(
                "Evaluator expected answer must be a string"
            )
        if not expected_answer.strip():
            self.logger.error(
                "Evaluator expected answer cannot be empty"
            )
            raise ValueError(
                "Evaluator expected answer cannot be empty"
            )
        expected_terms = self._get_content_terms(expected_answer)
        response_terms = self._get_content_terms(response)
        matched_terms = expected_terms.intersection(response_terms)
        missing_terms = expected_terms - response_terms
        score = len(matched_terms) / len(expected_terms)
        self.logger.info(
            f"Generation evaluation completed: "
            f"{len(matched_terms)}/{len(expected_terms)} expected terms matched"
        )
        return {
            "score": score,
            "expected_answer": expected_answer,
            "response": response,
            "matched_terms": list(matched_terms),
            "missing_terms": list(missing_terms)
        }

    def evaluate_citations(self, citations, available_sources):
        if not isinstance(citations, (list, tuple)):
            self.logger.error(
                "Evaluator citations must be a list or tuple"
            )
            raise ValueError(
                "Evaluator citations must be a list or tuple"
            )
        if not isinstance(available_sources, (list, tuple)):
            self.logger.error(
                "Evaluator available sources must be a list or tuple"
            )
            raise ValueError(
                "Evaluator available sources must be a list or tuple"
            )
        if not citations:
            self.logger.error(
                "Evaluator citations cannot be empty"
            )
            raise ValueError(
                "Evaluator citations cannot be empty"
            )
        if not available_sources:
            self.logger.error(
                "Evaluator available sources cannot be empty"
            )
            raise ValueError(
                "Evaluator available sources cannot be empty"
            )
        available = set()
        for source in available_sources:
            if isinstance(source, dict):
                if "source" not in source:
                    self.logger.error(
                        "Evaluator available source is missing source identity"
                    )
                    raise ValueError(
                        "Evaluator available source is missing source identity"
                    )
                source_name = source["source"]
            else:
                source_name = source
            if not isinstance(source_name, str):
                self.logger.error(
                    "Evaluator available source must contain a string identity"
                )
                raise ValueError(
                    "Evaluator available source must contain a string identity"
                )
            if not source_name.strip():
                self.logger.error(
                    "Evaluator available source identity cannot be empty"
                )
                raise ValueError(
                    "Evaluator available source identity cannot be empty"
                )
            available.add(source_name)
        cited = []
        valid = []
        invalid = []
        for citation in citations:
            if isinstance(citation, dict):
                if "source" not in citation:
                    self.logger.error(
                        "Evaluator citation is missing source identity"
                    )
                    raise ValueError(
                        "Evaluator citation is missing source identity"
                    )
                source_name = citation["source"]
            else:
                source_name = citation
            if not isinstance(source_name, str):
                self.logger.error(
                    "Evaluator citation source must be a string"
                )
                raise ValueError(
                    "Evaluator citation source must be a string"
                )
            if not source_name.strip():
                self.logger.error(
                    "Evaluator citation source cannot be empty"
                )
                raise ValueError(
                    "Evaluator citation source cannot be empty"
                )
            cited.append(source_name)
            if source_name in available:
                valid.append(source_name)
            else:
                invalid.append(source_name)
        score = len(valid) / len(cited)
        coverage = len(set(valid)) / len(available)
        self.logger.info(
            f"Citation evaluation completed: "
            f"{len(valid)}/{len(cited)} valid citations"
        )
        return {
            "score": score,
            "coverage": coverage,
            "cited_sources": cited,
            "valid_sources": valid,
            "invalid_sources": invalid
        }

    def evaluate_grounding(self, context, response):
        self._validate_context(context)
        self._validate_response(response)
        context_terms = self._get_content_terms(context)
        response_terms = self._get_content_terms(response)
        unsupported_terms = response_terms - context_terms
        supported_terms = response_terms.intersection(context_terms)
        score = len(supported_terms) / len(response_terms)
        self.logger.info(
            f"Grounding evaluation completed: "
            f"{len(supported_terms)}/{len(response_terms)} response terms supported"
        )
        return {
            "score": score,
            "supported_terms": list(supported_terms),
            "unsupported_terms": list(unsupported_terms),
            "context_terms": list(context_terms),
            "response_terms": list(response_terms)
        }

    def evaluate_metrics(
        self,
        retrieval_score,
        context_score,
        generation_score,
        citation_score,
        grounding_score
    ):
        scores = {
            "retrieval": retrieval_score,
            "context": context_score,
            "generation": generation_score,
            "citation": citation_score,
            "grounding": grounding_score
        }
        for name, score in scores.items():
            if not isinstance(score, (int, float)) or isinstance(score, bool):
                self.logger.error(
                    f"Evaluator {name} score must be numeric"
                )
                raise ValueError(
                    f"Evaluator {name} score must be numeric"
                )
            if score < 0 or score > 1:
                self.logger.error(
                    f"Evaluator {name} score must be between zero and one"
                )
                raise ValueError(
                    f"Evaluator {name} score must be between zero and one"
                )
        overall_score = round(sum(scores.values()) / len(scores), 6)
        self.logger.info(
            "Evaluation metrics aggregated successfully"
        )
        return {
            "retrieval": float(retrieval_score),
            "context": float(context_score),
            "generation": float(generation_score),
            "citation": float(citation_score),
            "grounding": float(grounding_score),
            "overall": float(overall_score)
        }

    def _validate_dataset(self, dataset):
        if not isinstance(dataset, (list, tuple)):
            self.logger.error(
                "Evaluator dataset must be a list or tuple"
            )
            raise ValueError(
                "Evaluator dataset must be a list or tuple"
            )
        if not dataset:
            self.logger.error(
                "Evaluator dataset cannot be empty"
            )
            raise ValueError(
                "Evaluator dataset cannot be empty"
            )
        required_fields = {
            "question",
            "context",
            "response",
            "expected_data"
        }
        for index, case in enumerate(dataset):
            if not isinstance(case, dict):
                self.logger.error(
                    f"Evaluator dataset case {index} must be a dictionary"
                )
                raise ValueError(
                    f"Evaluator dataset case {index} must be a dictionary"
                )
            missing_fields = required_fields - set(case.keys())
            if missing_fields:
                self.logger.error(
                    f"Evaluator dataset case {index} is missing required fields"
                )
                raise ValueError(
                    f"Evaluator dataset case {index} is missing required fields"
                )
            self.validate_inputs(
                case["question"],
                case["context"],
                case["response"],
                case["expected_data"]
            )
        return True

    def validate_dataset(self, dataset):
        self._validate_dataset(dataset)
        self.logger.info(
            f"Evaluation dataset validated successfully: {len(dataset)} cases"
        )
        return True

    def evaluate_dataset(self, dataset, evaluation_function):
        self._validate_dataset(dataset)
        if not callable(evaluation_function):
            self.logger.error(
                "Evaluator dataset evaluation function must be callable"
            )
            raise ValueError(
                "Evaluator dataset evaluation function must be callable"
            )
        results = []
        for index, case in enumerate(dataset):
            result = evaluation_function(case)
            if not isinstance(result, dict):
                self.logger.error(
                    f"Evaluator dataset case {index} result must be a dictionary"
                )
                raise ValueError(
                    f"Evaluator dataset case {index} result must be a dictionary"
                )
            results.append(result)
        self.logger.info(
            f"Evaluation dataset completed successfully: {len(results)} cases"
        )
        return results

    def evaluate(self, question, context, response):
        self.logger.info("Evaluation request received")
        return None