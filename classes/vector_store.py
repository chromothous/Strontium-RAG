import math

from classes.document import Document
from classes.logger import Logger


class VectorStore:
    def __init__(self, logger):
        if not isinstance(logger, Logger):
            raise ValueError("VectorStore logger must be a Logger")
        self.logger = logger
        self.vectors = {}
        self.dimension = None
        self.upsert_successes = 0
        self.upsert_failures = 0

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

    def add_many(self, embeddings):
        if not isinstance(embeddings, (list, tuple)):
            self.logger.error("VectorStore embeddings must be a list or tuple")
            raise ValueError("VectorStore embeddings must be a list or tuple")
        vector_ids = []
        for embedding in embeddings:
            vector_ids.append(self.add(embedding))
        self.logger.info(
            f"Vectors stored successfully: {len(vector_ids)}"
        )
        return vector_ids

    def get(self, vector_id):
        if not isinstance(vector_id, str) or not vector_id:
            raise ValueError("VectorStore vector ID must be a non-empty string")
        return self.vectors.get(vector_id)

    def remove(self, vector_id):
        if not isinstance(vector_id, str) or not vector_id:
            raise ValueError("VectorStore vector ID must be a non-empty string")
        if vector_id not in self.vectors:
            return False
        del self.vectors[vector_id]
        self.logger.info(f"Vector removed: {vector_id}")
        if not self.vectors:
            self.dimension = None
        return True

    def clear(self):
        count = len(self.vectors)
        self.vectors.clear()
        self.dimension = None
        self.logger.info(f"Vector store cleared: {count} vectors removed")
        return count

    def count(self):
        return len(self.vectors)

    def is_empty(self):
        return len(self.vectors) == 0

    def contains(self, vector_id):
        if not isinstance(vector_id, str) or not vector_id:
            raise ValueError("VectorStore vector ID must be a non-empty string")
        return vector_id in self.vectors

    def get_metadata(self, vector_id):
        if not isinstance(vector_id, str) or not vector_id:
            raise ValueError("VectorStore vector ID must be a non-empty string")
        record = self.vectors.get(vector_id)
        if record is None:
            return None
        return record["metadata"].copy()

    def get_record(self, vector_id):
        if not isinstance(vector_id, str) or not vector_id:
            raise ValueError("VectorStore vector ID must be a non-empty string")
        record = self.vectors.get(vector_id)
        if record is None:
            return None
        return {
            "chunk": record["chunk"],
            "embedding": record["embedding"].copy(),
            "metadata": record["metadata"].copy()
        }

    def update(self, embedding):
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
        if chunk.id not in self.vectors:
            return False
        vector = self._validate_vector(embedding["embedding"])
        metadata = embedding.get("metadata", {})
        if not isinstance(metadata, dict):
            self.logger.error("VectorStore metadata must be a dictionary")
            raise ValueError("VectorStore metadata must be a dictionary")
        self.vectors[chunk.id] = {
            "chunk": chunk,
            "embedding": vector,
            "metadata": metadata.copy()
        }
        self.logger.info(f"Vector updated: {chunk.id}")
        return True

    def upsert(self, embedding):
        if not isinstance(embedding, dict):
            self.logger.error("VectorStore embedding must be a dictionary")
            raise ValueError("VectorStore embedding must be a dictionary")
        if "chunk" not in embedding:
            self.logger.error("VectorStore embedding is missing chunk")
            raise ValueError("VectorStore embedding is missing chunk")
        chunk = embedding["chunk"]
        if not isinstance(chunk, Document):
            self.logger.error("VectorStore chunk must be a Document")
            raise ValueError("VectorStore chunk must be a Document")
        if chunk.id in self.vectors:
            self.update(embedding)
            return chunk.id
        return self.add(embedding)

    def get_all(self):
        return {
            vector_id: {
                "chunk": record["chunk"],
                "embedding": record["embedding"].copy(),
                "metadata": record["metadata"].copy()
            }
            for vector_id, record in self.vectors.items()
        }

    def upsert_many(self, embeddings):
        if not isinstance(embeddings, (list, tuple)):
            self.logger.error("VectorStore embeddings must be a list or tuple")
            raise ValueError("VectorStore embeddings must be a list or tuple")
        vector_ids = []
        self.upsert_successes = 0
        self.upsert_failures = 0
        for embedding in embeddings:
            try:
                vector_ids.append(self.upsert(embedding))
                self.upsert_successes += 1
            except ValueError as e:
                self.upsert_failures += 1
                self.logger.error(f"VectorStore skipped invalid embedding: {e}")
        self.logger.info(
            f"Vectors upserted successfully: {self.upsert_successes}, "
            f"invalid vectors skipped: {self.upsert_failures}"
        )
        return vector_ids

    def get_upsert_stats(self):
        return {
            "successes": self.upsert_successes,
            "failures": self.upsert_failures
        }

    def _cosine_similarity(self, vector_a, vector_b):
        if not isinstance(vector_a, (list, tuple)):
            raise ValueError("VectorStore first similarity vector must be a list or tuple")
        if not isinstance(vector_b, (list, tuple)):
            raise ValueError("VectorStore second similarity vector must be a list or tuple")
        if len(vector_a) != len(vector_b):
            raise ValueError("VectorStore similarity vectors must have the same dimension")
        if not vector_a or not vector_b:
            raise ValueError("VectorStore similarity vectors cannot be empty")
        if not all(isinstance(value, (int, float)) for value in vector_a):
            raise ValueError("VectorStore first similarity vector must contain only numeric values")
        if not all(isinstance(value, (int, float)) for value in vector_b):
            raise ValueError("VectorStore second similarity vector must contain only numeric values")
        dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
        magnitude_a = math.sqrt(sum(value * value for value in vector_a))
        magnitude_b = math.sqrt(sum(value * value for value in vector_b))
        if magnitude_a == 0 or magnitude_b == 0:
            raise ValueError("VectorStore similarity vectors cannot have zero magnitude")
        return dot_product / (magnitude_a * magnitude_b)

    def retrieve(self, query_vector):
        query_vector = self._validate_query_vector(query_vector)
        results = []
        for vector_id, record in self.vectors.items():
            if len(query_vector) != len(record["embedding"]):
                self.logger.error(
                    f"VectorStore dimension mismatch during retrieval: {vector_id}"
                )
                raise ValueError("VectorStore query and stored vectors must have the same dimension")
            similarity = self._cosine_similarity(
                query_vector,
                record["embedding"]
            )
            results.append({
                "id": vector_id,
                "chunk": record["chunk"],
                "embedding": record["embedding"].copy(),
                "metadata": record["metadata"].copy(),
                "similarity": similarity
            })
        results.sort(key=lambda result: result["similarity"], reverse=True)
        return results

    def _validate_query_vector(self, query_vector):
        if not isinstance(query_vector, (list, tuple)):
            self.logger.error("VectorStore query vector must be a list or tuple")
            raise ValueError("VectorStore query vector must be a list or tuple")
        if not query_vector:
            self.logger.error("VectorStore query vector cannot be empty")
            raise ValueError("VectorStore query vector cannot be empty")
        if not all(isinstance(value, (int, float)) for value in query_vector):
            self.logger.error("VectorStore query vector must contain only numeric values")
            raise ValueError("VectorStore query vector must contain only numeric values")
        if self.dimension is not None and len(query_vector) != self.dimension:
            self.logger.error("VectorStore query vector has an invalid dimension")
            raise ValueError("VectorStore query vector must match the vector store dimension")
        return list(query_vector)