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

    def cite(self, answer, sources):
        self.logger.info("Citation request received")
        return None