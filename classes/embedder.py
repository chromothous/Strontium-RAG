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
        embeddings = []
        self.logger.info(f"Embedding {len(chunks)} chunks")
        for chunk in chunks:
            if not isinstance(chunk, Document):
                self.logger.error("Embedder input must contain only Documents")
                raise ValueError("Embedder input must contain only Documents")
            vector = self.provider.embed(chunk.content)
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
            embeddings.append({
                "chunk": chunk,
                "embedding": list(vector)
            })
        self.logger.info(
            f"Chunks embedded successfully: {len(embeddings)}"
        )
        return embeddings