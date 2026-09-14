from classes.logger import Logger


class Citation:
    def __init__(self, logger):
        if not isinstance(logger, Logger):
            raise ValueError("Citation logger must be a Logger")
        self.logger = logger

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
            self._validate_source_item(source)
            propagated.append({
                "source": source["source"],
                "document_id": source["document_id"],
                "chunk_id": source["chunk_id"]
            })
        self.logger.info(
            f"Citation source identities propagated: {len(propagated)} sources"
        )
        return propagated

    def build_citation_metadata(self, source):
        self._validate_source_item(source)
        metadata = source.get("metadata", {})
        if not isinstance(metadata, dict):
            self.logger.error("Citation source metadata must be a dictionary")
            raise ValueError("Citation source metadata must be a dictionary")
        return {
            "source": source["source"],
            "document_id": source["document_id"],
            "chunk_id": source["chunk_id"],
            "metadata": metadata.copy()
        }

    def place_citation(self, answer, citation):
        if not isinstance(answer, str):
            self.logger.error("Citation answer must be a string")
            raise ValueError("Citation answer must be a string")
        if not answer.strip():
            self.logger.error("Citation answer cannot be empty")
            raise ValueError("Citation answer cannot be empty")
        if not isinstance(citation, dict):
            self.logger.error("Citation must be a dictionary")
            raise ValueError("Citation must be a dictionary")
        self._validate_source_item(citation)
        formatted_citation = f"[{citation['source']}]"
        placed = f"{answer} {formatted_citation}"
        self.logger.info("Citation placed successfully")
        return placed

    def cite(self, answer, sources):
        self.logger.info("Citation request received")
        return None