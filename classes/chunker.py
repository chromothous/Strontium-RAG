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

    def _find_boundary(self, content, start):
        target = start + self.chunk_size
        if target >= len(content):
            return len(content)
        boundary = content.rfind(" ", start, target + 1)
        if boundary > start:
            return boundary
        return target

    def chunk(self, document):
        if not isinstance(document, Document):
            self.logger.error("Chunker document must be a Document")
            raise ValueError("Chunker document must be a Document")
        self.logger.info(f"Chunking document: {document.source}")
        chunks = []
        content = document.content
        start = 0
        while start < len(content):
            end = self._find_boundary(content, start)
            chunk_content = content[start:end].strip()
            if not chunk_content:
                start = end + 1
                continue
            chunk_metadata = document.metadata.copy()
            chunk_metadata["document_id"] = document.id
            chunk_metadata["chunk_index"] = len(chunks)
            chunk_metadata["chunk_start"] = start
            chunk_metadata["chunk_end"] = end
            chunk = Document(
                chunk_content,
                document.source,
                chunk_metadata
            )
            chunks.append(chunk)
            start = end
            while start < len(content) and content[start].isspace():
                start += 1
        self.logger.info(
            f"Document chunked successfully: {document.source} "
            f"({len(chunks)} chunks)"
        )
        return chunks