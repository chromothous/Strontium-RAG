from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, text):
        raise NotImplementedError

    def embed_many(self, texts):
        return [self.embed(text) for text in texts]