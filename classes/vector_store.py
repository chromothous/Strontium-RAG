from classes.document import Document
from classes.logger import Logger


class VectorStore:
    def __init__(self, logger):
        if not isinstance(logger, Logger):
            raise ValueError("VectorStore logger must be a Logger")
        self.logger = logger
        self.vectors = {}
        self.dimension = None

    def _validate_vector(self, vector):
        if not isinstance(vector, (list, tuple)):
            raise ValueError("VectorStore embedding must be a list or tuple")
        if not vector:
            raise ValueError("VectorStore embedding vector cannot be empty")
        if not all(isinstance(value, (int, float)) for value in vector):
            raise ValueError("VectorStore embedding vector must contain only numeric values")
        if self.dimension is not None and len(vector) != self.dimension:
            raise ValueError("VectorStore embedding vectors must have the same dimension")
        return list(vector)

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
        if not isinstance(chunk, Document):
            self.logger.error("VectorStore chunk must be a Document")
            raise ValueError("VectorStore chunk must be a Document")
        vector = self._validate_vector(embedding["embedding"])
        metadata = embedding.get("metadata", {})
        if not isinstance(metadata, dict):
            self.logger.error("VectorStore metadata must be a dictionary")
            raise ValueError("VectorStore metadata must be a dictionary")
        if self.dimension is None:
            self.dimension = len(vector)
        vector_id = chunk.id
        self.vectors[vector_id] = {
            "chunk": chunk,
            "embedding": vector,
            "metadata": metadata.copy()
        }
        self.logger.info(f"Vector stored: {vector_id}")
        return vector_id

    def get(self, vector_id):
        if not isinstance(vector_id, str) or not vector_id:
            raise ValueError("VectorStore vector ID must be a non-empty string")
        return self.vectors.get(vector_id)