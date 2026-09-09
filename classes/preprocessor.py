import re

from classes.document import Document
from classes.logger import Logger


class Preprocessor:
    def __init__(self, logger):
        if not isinstance(logger, Logger):
            raise ValueError("Preprocessor logger must be a Logger")
        self.logger = logger

    def process(self, document):
        if not isinstance(document, Document):
            self.logger.error("Preprocessor document must be a Document")
            raise ValueError("Preprocessor document must be a Document")
        self.logger.info(f"Preprocessing document: {document.source}")
        content = document.content
        content = content.replace("\ufeff", "")
        content = content.replace("\u00a0", " ")
        content = content.replace("\u200b", "")
        content = content.replace("\r\n", "\n").replace("\r", "\n")
        content = re.sub(r"[ \t]+", " ", content)
        content = re.sub(r"\n[ \t]+", "\n", content)
        content = re.sub(r"[ \t]+\n", "\n", content)
        content = re.sub(r"\n{3,}", "\n\n", content)
        content = content.strip()
        if not isinstance(content, str) or not content:
            self.logger.error(f"Preprocessing produced empty content: {document.source}")
            raise ValueError("Preprocessing produced empty document content")
        if not isinstance(document.source, str) or not document.source:
            self.logger.error("Preprocessor document source is invalid")
            raise ValueError("Preprocessor document source is invalid")
        if not isinstance(document.metadata, dict):
            self.logger.error("Preprocessor document metadata is invalid")
            raise ValueError("Preprocessor document metadata is invalid")
        processed = Document(
            content,
            document.source,
            document.metadata.copy()
        )
        processed.id = document.id
        return processed