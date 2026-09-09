from classes.document import Document
from classes.embedding_provider import EmbeddingProvider
from classes.logger import Logger


class Embedder:
    def __init__(self, provider, logger):
        if not isinstance(provider, EmbeddingProvider):
            raise ValueError("Embedder provider must be an EmbeddingProvider")
        if not isinstance(logger, Logger):
            raise ValueError("Embedder logger must be a Logger")
        self.provider = provider
        self.logger = logger

    def embed(self, chunks):
        if not isinstance(chunks, (list, tuple)):
            self.logger.error("Embedder chunks must be a list or tuple")
            raise ValueError("Embedder chunks must be a list or tuple")
        self.logger.info(f"Embedding {len(chunks)} chunks")
        for chunk in chunks:
            if not isinstance(chunk, Document):
                self.logger.error("Embedder input must contain only Documents")
                raise ValueError("Embedder input must contain only Documents")
        if not chunks:
            self.logger.info("No chunks provided for embedding")
            return []
        texts = [chunk.content for chunk in chunks]
        vectors = self.provider.embed_many(texts)
        if not isinstance(vectors, (list, tuple)):
            self.logger.error("Embedding provider returned an invalid batch")
            raise ValueError("Embedding provider must return a list or tuple")
        if len(vectors) != len(chunks):
            self.logger.error("Embedding provider returned an incorrect batch size")
            raise ValueError("Embedding provider must return one vector per chunk")
        embeddings = []
        expected_dimension = None
        for chunk, vector in zip(chunks, vectors):
            if not isinstance(vector, (list, tuple)):
                self.logger.error(
                    f"Embedding provider returned an invalid vector: {chunk.source}"
                )
                raise ValueError("Embedding provider must return a list or tuple")
            if not vector:
                self.logger.error(
                    f"Embedding provider returned an empty vector: {chunk.source}"
                )
                raise ValueError("Embedding provider must return a non-empty vector")
            if not all(isinstance(value, (int, float)) for value in vector):
                self.logger.error(
                    f"Embedding provider returned non-numeric values: {chunk.source}"
                )
                raise ValueError("Embedding vector must contain only numeric values")
            if expected_dimension is None:
                expected_dimension = len(vector)
            elif len(vector) != expected_dimension:
                self.logger.error(
                    f"Embedding dimension mismatch: {chunk.source}"
                )
                raise ValueError("All embedding vectors must have the same dimension")
            embeddings.append({
                "chunk": chunk,
                "embedding": list(vector)
            })
        self.logger.info(
            f"Chunks embedded successfully: {len(embeddings)}"
        )
        return embeddings