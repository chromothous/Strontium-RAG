from classes.logger import Logger


class VectorStore:
    def __init__(self, logger):
        if not isinstance(logger, Logger):
            raise ValueError("VectorStore logger must be a Logger")
        self.logger = logger
        self.vectors = {}

    def add(self, embedding):
        if not isinstance(embedding, dict):
            self.logger.error("VectorStore embedding must be a dictionary")
            raise ValueError("VectorStore embedding must be a dictionary")
        if "chunk" not in embedding:
            self.logger.error("VectorStore embedding is missing chunk")
            raise ValueError("VectorStore embedding is missing chunk")
        if "embedding" not in embedding:
            self.logger.error("VectorStore embedding is missing vector")
            raise ValueError("VectorStore embedding is missing vector")
        chunk = embedding["chunk"]
        vector = embedding["embedding"]
        if not vector:
            self.logger.error("VectorStore embedding vector cannot be empty")
            raise ValueError("VectorStore embedding vector cannot be empty")
        vector_id = chunk.id
        self.vectors[vector_id] = {
            "chunk": chunk,
            "embedding": list(vector),
            "metadata": embedding.get("metadata", {}).copy()
        }
        self.logger.info(f"Vector stored: {vector_id}")
        return vector_id

    def get(self, vector_id):
        if not isinstance(vector_id, str) or not vector_id:
            raise ValueError("VectorStore vector ID must be a non-empty string")
        return self.vectors.get(vector_id)