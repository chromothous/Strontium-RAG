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
        self.last_batch_stats = {
            "attempted": 0,
            "successful": 0,
            "failed": 0
        }

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
        attempted = len(paths)
        successful = 0
        failed = 0
        for path in paths:
            try:
                documents.append(self.load(path))
                successful += 1
            except Exception as e:
                failed += 1
                self.logger.error(f"Failed to load document: {path} - {e}")
        self.last_batch_stats = {
            "attempted": attempted,
            "successful": successful,
            "failed": failed
        }
        self.logger.info(f"Loaded {successful}/{attempted} documents successfully")
        return documents

    def get_batch_stats(self):
        return self.last_batch_stats.copy()

    def find_files(self, directory):
        if not isinstance(directory, str) or not directory:
            self.logger.error("Loader directory must be a non-empty string")
            raise ValueError("Loader directory must be a non-empty string")
        if not os.path.isdir(directory):
            self.logger.error(f"Loader directory not found: {directory}")
            raise FileNotFoundError(f"Loader directory not found: {directory}")
        self.logger.info(f"Searching for documents in: {directory}")
        paths = []
        for root, directories, files in os.walk(directory):
            for filename in files:
                if os.path.splitext(filename)[1].lower() == ".txt":
                    paths.append(os.path.join(root, filename))
        self.logger.info(f"Found {len(paths)} documents in: {directory}")
        return paths