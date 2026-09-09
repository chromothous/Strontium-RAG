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
        content = re.sub(r"[ \t]+", " ", document.content).strip()
        processed = Document(
            content,
            document.source,
            document.metadata.copy()
        )
        processed.id = document.id
        return processed