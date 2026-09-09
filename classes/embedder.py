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
        self.last_embedding_stats = {
            "attempted": 0,
            "successful": 0,
            "failed": 0
        }
        self.last_embedding_failures = []

    def _validate_vector(self, vector, expected_dimension=None):
        if not isinstance(vector, (list, tuple)):
            raise ValueError("Embedding provider must return a list or tuple")
        if not vector:
            raise ValueError("Embedding provider must return a non-empty vector")
        if not all(isinstance(value, (int, float)) for value in vector):
            raise ValueError("Embedding vector must contain only numeric values")
        if expected_dimension is not None and len(vector) != expected_dimension:
            raise ValueError("All embedding vectors must have the same dimension")
        return list(vector)

    def _build_result(self, chunk, vector):
        metadata = chunk.metadata.copy()
        metadata["chunk_id"] = chunk.id
        metadata["document_id"] = chunk.metadata.get("document_id")
        metadata["source"] = chunk.source
        return {
            "chunk": chunk,
            "embedding": vector,
            "metadata": metadata
        }

    def _record_failure(self, chunk, error):
        self.last_embedding_stats["failed"] += 1
        self.last_embedding_failures.append({
            "chunk_id": chunk.id,
            "source": chunk.source,
            "error": str(error)
        })
        self.logger.error(
            f"Failed to embed chunk: {chunk.source} - {error}"
        )

    def embed(self, chunks):
        if not isinstance(chunks, (list, tuple)):
            self.logger.error("Embedder chunks must be a list or tuple")
            raise ValueError("Embedder chunks must be a list or tuple")
        self.logger.info(f"Embedding {len(chunks)} chunks")
        for chunk in chunks:
            if not isinstance(chunk, Document):
                self.logger.error("Embedder input must contain only Documents")
                raise ValueError("Embedder input must contain only Documents")
        self.last_embedding_stats = {
            "attempted": len(chunks),
            "successful": 0,
            "failed": 0
        }
        self.last_embedding_failures = []
        if not chunks:
            self.logger.info("No chunks provided for embedding")
            return []
        texts = [chunk.content for chunk in chunks]
        try:
            vectors = self.provider.embed_many(texts)
        except Exception as e:
            self.logger.warning(
                "Batch embedding failed; retrying chunks individually"
            )
            embeddings = []
            expected_dimension = None
            for chunk in chunks:
                try:
                    vector = self.provider.embed(chunk.content)
                except Exception as individual_error:
                    self._record_failure(chunk, individual_error)
                    continue
                vector = self._validate_vector(vector, expected_dimension)
                if expected_dimension is None:
                    expected_dimension = len(vector)
                embeddings.append(self._build_result(chunk, vector))
                self.last_embedding_stats["successful"] += 1
            self.logger.info(
                f"Chunks embedded successfully: "
                f"{self.last_embedding_stats['successful']}/"
                f"{self.last_embedding_stats['attempted']}"
            )
            return embeddings
        if not isinstance(vectors, (list, tuple)):
            self.logger.error("Embedding provider returned an invalid batch")
            raise ValueError("Embedding provider must return a list or tuple")
        if len(vectors) != len(chunks):
            self.logger.error("Embedding provider returned an incorrect batch size")
            raise ValueError("Embedding provider must return one vector per chunk")
        embeddings = []
        expected_dimension = None
        for chunk, vector in zip(chunks, vectors):
            vector = self._validate_vector(vector, expected_dimension)
            if expected_dimension is None:
                expected_dimension = len(vector)
            embeddings.append(self._build_result(chunk, vector))
            self.last_embedding_stats["successful"] += 1
        self.logger.info(
            f"Chunks embedded successfully: "
            f"{self.last_embedding_stats['successful']}/"
            f"{self.last_embedding_stats['attempted']}"
        )
        return embeddings

    def get_embedding_stats(self):
        return self.last_embedding_stats.copy()

    def get_embedding_failures(self):
        return self.last_embedding_failures.copy()