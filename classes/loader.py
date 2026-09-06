import os

from classes.document import Document
from classes.logger import Logger


class Loader:
    def __init__(self, logger):
        if not isinstance(logger, Logger):
            raise ValueError("Loader logger must be a Logger")
        self.logger = logger

    def load(self, path):
        if not isinstance(path, str) or not path:
            self.logger.error("Loader path must be a non-empty string")
            raise ValueError("Loader path must be a non-empty string")
        if not os.path.isfile(path):
            self.logger.error(f"Document file not found: {path}")
            raise FileNotFoundError(f"Document file not found: {path}")
        if os.path.splitext(path)[1].lower() != ".txt":
            self.logger.error(f"Unsupported document type: {path}")
            raise ValueError("Loader only supports .txt files")
        self.logger.info(f"Loading document: {path}")
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()
        if not content:
            self.logger.warning(f"Document is empty: {path}")
            raise ValueError("Document content cannot be empty")
        document = Document(content, path)
        self.logger.info(f"Document loaded successfully: {path}")
        return document