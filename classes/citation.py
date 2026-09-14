from classes.logger import Logger


class Citation:
    def __init__(self, logger):
        if not isinstance(logger, Logger):
            raise ValueError("Citation logger must be a Logger")
        self.logger = logger

    def _normalize_source_item(self, source):
        if not isinstance(source, dict):
            self.logger.error("Citation source must be a dictionary")
            raise ValueError("Citation source must be a dictionary")
        if "chunk" in source:
            chunk = source["chunk"]
            if not hasattr(chunk, "content"):
                self.logger.error("Citation source chunk must contain content")
                raise ValueError("Citation source chunk must contain content")
            if not hasattr(chunk, "source"):
                self.logger.error("Citation source chunk must contain source identity")
                raise ValueError("Citation source chunk must contain source identity")
            metadata = getattr(chunk, "metadata", {})
            if not isinstance(metadata, dict):
                self.logger.error("Citation source chunk metadata must be a dictionary")
                raise ValueError("Citation source chunk metadata must be a dictionary")
            document_id = metadata.get("document_id")
            chunk_id = getattr(chunk, "id", None)
            if document_id is None:
                self.logger.error("Citation source chunk is missing document identity")
                raise ValueError("Citation source chunk is missing document identity")
            if chunk_id is None:
                self.logger.error("Citation source chunk is missing chunk identity")
                raise ValueError("Citation source chunk is missing chunk identity")
            return {
                "content": chunk.content,
                "source": chunk.source,
                "document_id": document_id,
                "chunk_id": chunk_id,
                "metadata": metadata.copy()
            }
        return source.copy()

    def _validate_source_item(self, source):
        if not isinstance(source, dict):
            self.logger.error("Citation source must be a dictionary")
            raise ValueError("Citation source must be a dictionary")
        if "source" not in source:
            self.logger.error("Citation source is missing source identity")
            raise ValueError("Citation source is missing source identity")
        if not isinstance(source["source"], str) or not source["source"]:
            self.logger.error("Citation source identity must be a non-empty string")
            raise ValueError("Citation source identity must be a non-empty string")
        if "document_id" not in source:
            self.logger.error("Citation source is missing document identity")
            raise ValueError("Citation source is missing document identity")
        if source["document_id"] is None:
            self.logger.error("Citation document identity cannot be None")
            raise ValueError("Citation document identity cannot be None")
        if "chunk_id" not in source:
            self.logger.error("Citation source is missing chunk identity")
            raise ValueError("Citation source is missing chunk identity")
        if source["chunk_id"] is None:
            self.logger.error("Citation chunk identity cannot be None")
            raise ValueError("Citation chunk identity cannot be None")

    def propagate_source_identity(self, sources):
        if not isinstance(sources, (list, tuple)):
            self.logger.error("Citation sources must be a list or tuple")
            raise ValueError("Citation sources must be a list or tuple")
        propagated = []
        for source in sources:
            normalized = self._normalize_source_item(source)
            self._validate_source_item(normalized)
            propagated.append({
                "source": normalized["source"],
                "document_id": normalized["document_id"],
                "chunk_id": normalized["chunk_id"]
            })
        self.logger.info(
            f"Citation source identities propagated: {len(propagated)} sources"
        )
        return propagated

    def build_citation_metadata(self, source):
        normalized = self._normalize_source_item(source)
        self._validate_source_item(normalized)
        metadata = normalized.get("metadata", {})
        if not isinstance(metadata, dict):
            self.logger.error("Citation source metadata must be a dictionary")
            raise ValueError("Citation source metadata must be a dictionary")
        return {
            "source": normalized["source"],
            "document_id": normalized["document_id"],
            "chunk_id": normalized["chunk_id"],
            "metadata": metadata.copy()
        }

    def place_citation(self, answer, citation):
        if not isinstance(answer, str):
            self.logger.error("Citation answer must be a string")
            raise ValueError("Citation answer must be a string")
        if not answer.strip():
            self.logger.error("Citation answer cannot be empty")
            raise ValueError("Citation answer cannot be empty")
        normalized = self._normalize_source_item(citation)
        self._validate_source_item(normalized)
        formatted_citation = f"[{normalized['source']}]"
        placed = f"{answer} {formatted_citation}"
        self.logger.info("Citation placed successfully")
        return placed

    def place_citations(self, answer, citations):
        if not isinstance(answer, str):
            self.logger.error("Citation answer must be a string")
            raise ValueError("Citation answer must be a string")
        if not answer.strip():
            self.logger.error("Citation answer cannot be empty")
            raise ValueError("Citation answer cannot be empty")
        if not isinstance(citations, (list, tuple)):
            self.logger.error("Citation sources must be a list or tuple")
            raise ValueError("Citation sources must be a list or tuple")
        if not citations:
            self.logger.error("Citation sources cannot be empty")
            raise ValueError("Citation sources cannot be empty")
        formatted_citations = []
        for citation in citations:
            normalized = self._normalize_source_item(citation)
            self._validate_source_item(normalized)
            formatted_citations.append(f"[{normalized['source']}]")
        placed = f"{answer} {' '.join(formatted_citations)}"
        self.logger.info(
            f"Multiple citations placed successfully: {len(citations)} sources"
        )
        return placed

    def place_unique_citations(self, answer, citations):
        if not isinstance(answer, str):
            self.logger.error("Citation answer must be a string")
            raise ValueError("Citation answer must be a string")
        if not answer.strip():
            self.logger.error("Citation answer cannot be empty")
            raise ValueError("Citation answer cannot be empty")
        if not isinstance(citations, (list, tuple)):
            self.logger.error("Citation sources must be a list or tuple")
            raise ValueError("Citation sources must be a list or tuple")
        if not citations:
            self.logger.error("Citation sources cannot be empty")
            raise ValueError("Citation sources cannot be empty")
        unique_citations = []
        seen_sources = set()
        for citation in citations:
            normalized = self._normalize_source_item(citation)
            self._validate_source_item(normalized)
            source_key = (
                normalized["source"],
                normalized["document_id"]
            )
            if source_key in seen_sources:
                continue
            seen_sources.add(source_key)
            unique_citations.append(f"[{normalized['source']}]")
        placed = f"{answer} {' '.join(unique_citations)}"
        self.logger.info(
            f"Unique citations placed successfully: {len(unique_citations)} sources"
        )
        return placed

    def validate_completeness(self, sources, citations):
        if not isinstance(sources, (list, tuple)):
            self.logger.error("Citation sources must be a list or tuple")
            raise ValueError("Citation sources must be a list or tuple")
        if not sources:
            self.logger.error("Citation sources cannot be empty")
            raise ValueError("Citation sources cannot be empty")
        if not isinstance(citations, (list, tuple)):
            self.logger.error("Citation citations must be a list or tuple")
            raise ValueError("Citation citations must be a list or tuple")
        required_sources = set()
        cited_sources = set()
        for source in sources:
            normalized = self._normalize_source_item(source)
            self._validate_source_item(normalized)
            required_sources.add(
                (
                    normalized["source"],
                    normalized["document_id"]
                )
            )
        for citation in citations:
            normalized = self._normalize_source_item(citation)
            self._validate_source_item(normalized)
            cited_sources.add(
                (
                    normalized["source"],
                    normalized["document_id"]
                )
            )
        missing_sources = required_sources - cited_sources
        if missing_sources:
            self.logger.error(
                f"Citation completeness check found missing sources: {len(missing_sources)}"
            )
            return False
        self.logger.info(
            "Citation completeness check passed"
        )
        return True

    def validate_context_consistency(self, sources, citations):
        if not isinstance(sources, (list, tuple)):
            self.logger.error("Citation sources must be a list or tuple")
            raise ValueError("Citation sources must be a list or tuple")
        if not isinstance(citations, (list, tuple)):
            self.logger.error("Citation citations must be a list or tuple")
            raise ValueError("Citation citations must be a list or tuple")
        context_sources = set()
        for source in sources:
            normalized = self._normalize_source_item(source)
            self._validate_source_item(normalized)
            context_sources.add(
                (
                    normalized["source"],
                    normalized["document_id"]
                )
            )
        for citation in citations:
            normalized = self._normalize_source_item(citation)
            self._validate_source_item(normalized)
            citation_source = (
                normalized["source"],
                normalized["document_id"]
            )
            if citation_source not in context_sources:
                self.logger.error(
                    "Citation references a source not present in the supplied context"
                )
                return False
        self.logger.info(
            "Citation and context consistency check passed"
        )
        return True

    def validate_citation(self, citation):
        normalized = self._normalize_source_item(citation)
        self._validate_source_item(normalized)
        metadata = normalized.get("metadata", {})
        if not isinstance(metadata, dict):
            self.logger.error("Citation metadata must be a dictionary")
            raise ValueError("Citation metadata must be a dictionary")
        self.logger.info("Citation structure validated successfully")
        return True

    def place_citations_safe(self, answer, citations):
        if not isinstance(answer, str):
            self.logger.error("Citation answer must be a string")
            raise ValueError("Citation answer must be a string")
        if not answer.strip():
            self.logger.error("Citation answer cannot be empty")
            raise ValueError("Citation answer cannot be empty")
        try:
            placed = self.place_unique_citations(
                answer,
                citations
            )
            return {
                "answer": placed,
                "citations": list(citations),
                "error": None
            }
        except Exception as e:
            self.logger.error(
                f"Citation generation failed: {e}"
            )
            return {
                "answer": answer,
                "citations": [],
                "error": str(e)
            }

    def cite_complete(self, answer, sources):
        if not isinstance(answer, str):
            self.logger.error("Citation answer must be a string")
            raise ValueError("Citation answer must be a string")
        if not answer.strip():
            self.logger.error("Citation answer cannot be empty")
            raise ValueError("Citation answer cannot be empty")
        if not isinstance(sources, (list, tuple)):
            self.logger.error("Citation sources must be a list or tuple")
            raise ValueError("Citation sources must be a list or tuple")
        if not sources:
            self.logger.error("Citation sources cannot be empty")
            raise ValueError("Citation sources cannot be empty")
        normalized_sources = [
            self._normalize_source_item(source)
            for source in sources
        ]
        propagated = self.propagate_source_identity(normalized_sources)
        citation_metadata = []
        for source in normalized_sources:
            citation_metadata.append(
                self.build_citation_metadata(source)
            )
        assert self.validate_context_consistency(
            normalized_sources,
            propagated
        )
        assert self.validate_completeness(
            normalized_sources,
            propagated
        )
        for citation in citation_metadata:
            self.validate_citation(citation)
        placed = self.place_unique_citations(
            answer,
            citation_metadata
        )
        self.logger.info(
            "Complete citation pipeline executed successfully"
        )
        return {
            "answer": placed,
            "citations": citation_metadata
        }

    def cite(self, answer, sources):
        self.logger.info("Citation request received")
        return None