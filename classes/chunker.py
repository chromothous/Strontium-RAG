from classes.document import Document
from classes.logger import Logger


class Chunker:
    def __init__(self, logger, chunk_size=500):
        if not isinstance(logger, Logger):
            raise ValueError("Chunker logger must be a Logger")
        if not isinstance(chunk_size, int) or chunk_size <= 0:
            raise ValueError("Chunker chunk size must be a positive integer")
        self.logger = logger
        self.chunk_size = chunk_size

    def chunk(self, document):
        if not isinstance(document, Document):
            self.logger.error("Chunker document must be a Document")
            raise ValueError("Chunker document must be a Document")
        self.logger.info(f"Chunking document: {document.source}")
        chunks = []
        content = document.content
        for index in range(0, len(content), self.chunk_size):
            chunk_content = content[index:index + self.chunk_size]
            chunk_metadata = document.metadata.copy()
            chunk_metadata["document_id"] = document.id
            chunk_metadata["chunk_index"] = len(chunks)
            chunk_metadata["chunk_start"] = index
            chunk_metadata["chunk_end"] = index + len(chunk_content)
            chunk = Document(
                chunk_content,
                document.source,
                chunk_metadata
            )
            chunks.append(chunk)
        self.logger.info(
            f"Document chunked successfully: {document.source} "
            f"({len(chunks)} chunks)"
        )
        return chunks