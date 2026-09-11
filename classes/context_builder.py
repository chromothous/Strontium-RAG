from classes.logger import Logger


class ContextBuilder:
    def __init__(self, logger):
        if not isinstance(logger, Logger):
            raise ValueError("ContextBuilder logger must be a Logger")
        self.logger = logger

    def build(self, results):
        if not isinstance(results, (list, tuple)):
            self.logger.error("ContextBuilder results must be a list or tuple")
            raise ValueError("ContextBuilder results must be a list or tuple")
        context_parts = []
        for result in results:
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
            context_parts.append(chunk.content)
        context = "\n\n".join(context_parts)
        self.logger.info(
            f"Context constructed successfully: {len(context_parts)} chunks"
        )
        return context