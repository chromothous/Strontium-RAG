from classes.document import Document
from classes.logger import Logger


class Chunker:
    def __init__(self, logger, chunk_size=500, chunk_overlap=0):
        if not isinstance(logger, Logger):
            raise ValueError("Chunker logger must be a Logger")
        if not isinstance(chunk_size, int) or chunk_size <= 0:
            raise ValueError("Chunker chunk size must be a positive integer")
        if not isinstance(chunk_overlap, int) or chunk_overlap < 0:
            raise ValueError("Chunker chunk overlap must be a non-negative integer")
        if chunk_overlap >= chunk_size:
            raise ValueError("Chunker chunk overlap must be smaller than chunk size")
        self.logger = logger
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

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
            if end >= len(content):
                break
            next_start = end - self.chunk_overlap
            if next_start <= start:
                next_start = end
            while next_start < len(content) and content[next_start].isspace():
                next_start += 1
            start = next_start
        self.logger.info(
            f"Document chunked successfully: {document.source} "
            f"({len(chunks)} chunks)"
        )
        return chunks