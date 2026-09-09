import os
import codecs

from classes.document import Document
from classes.logger import Logger

class Loader:
    def __init__(self, logger, encoding="utf-8"):
        if not isinstance(logger, Logger):
            raise ValueError("Loader logger must be a Logger")
        if not isinstance(encoding, str) or not encoding:
            raise ValueError("Loader encoding must be a non-empty string")
        try:
            codecs.lookup(encoding)
        except LookupError:
            raise ValueError(f"Unsupported loader encoding: {encoding}")
        self.logger = logger
        self.encoding = encoding

    def read_file(self, path):
        self.logger.info(f"Reading file: {path}")
        try:
            with open(path, "r", encoding=self.encoding) as file:
                return file.read()
        except Exception as e:
            self.logger.error(f"Failed to read file: {path} - {e}")
            raise e

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
        content = self.read_file(path)
        if not content:
            self.logger.warning(f"Document is empty: {path}")
            raise ValueError("Document content cannot be empty")
        metadata = {
            "file_name": os.path.basename(path),
            "file_type": os.path.splitext(path)[1].lower(),
            "file_size": os.path.getsize(path)
        }
        document = Document(content, path, metadata)
        self.logger.info(f"Document loaded successfully: {path}")
        return document

    def load_many(self, paths):
        if not isinstance(paths, (list, tuple)):
            self.logger.error("Loader paths must be a list or tuple")
            raise ValueError("Loader paths must be a list or tuple")
        self.logger.info(f"Loading {len(paths)} documents")
        documents = []
        for path in paths:
            documents.append(self.load(path))
        self.logger.info(f"Loaded {len(documents)} documents successfully")
        return documents