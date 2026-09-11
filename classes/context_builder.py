from classes.logger import Logger


class ContextBuilder:
    def __init__(self, logger):
        if not isinstance(logger, Logger):
            raise ValueError("ContextBuilder logger must be a Logger")
        self.logger = logger

    def _validate_result(self, result):
        if not isinstance(result, dict):
            self.logger.error("ContextBuilder result must be a dictionary")
            raise ValueError("ContextBuilder result must be a dictionary")
        if "chunk" not in result:
            self.logger.error("ContextBuilder result is missing chunk")
            raise ValueError("ContextBuilder result is missing chunk")
        chunk = result["chunk"]
        if not hasattr(chunk, "content"):
            self.logger.error("ContextBuilder result chunk must contain content")
            raise ValueError("ContextBuilder result chunk must contain content")
        if not isinstance(chunk.content, str):
            self.logger.error("ContextBuilder chunk content must be a string")
            raise ValueError("ContextBuilder chunk content must be a string")
        if not chunk.content:
            self.logger.error("ContextBuilder chunk content cannot be empty")
            raise ValueError("ContextBuilder chunk content cannot be empty")
        return chunk

    def _build_item(self, result):
        chunk = self._validate_result(result)
        metadata = getattr(chunk, "metadata", {})
        if not isinstance(metadata, dict):
            self.logger.error("ContextBuilder chunk metadata must be a dictionary")
            raise ValueError("ContextBuilder chunk metadata must be a dictionary")
        return {
            "content": chunk.content,
            "source": getattr(chunk, "source", None),
            "document_id": metadata.get("document_id"),
            "chunk_id": getattr(chunk, "id", None)
        }

    def build_items(self, results):
        if not isinstance(results, (list, tuple)):
            self.logger.error("ContextBuilder results must be a list or tuple")
            raise ValueError("ContextBuilder results must be a list or tuple")
        items = []
        for result in results:
            items.append(self._build_item(result))
        self.logger.info(
            f"Context items constructed successfully: {len(items)} chunks"
        )
        return items

    def build(self, results):
        if not isinstance(results, (list, tuple)):
            self.logger.error("ContextBuilder results must be a list or tuple")
            raise ValueError("ContextBuilder results must be a list or tuple")
        context_parts = []
        for result in results:
            chunk = self._validate_result(result)
            context_parts.append(chunk.content)
        context = "\n\n".join(context_parts)
        self.logger.info(
            f"Context constructed successfully: {len(context_parts)} chunks"
        )
        return context