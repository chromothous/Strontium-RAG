import os

from classes.loader import Loader
from classes.logger import Logger


class Ingestion:
    def __init__(self, loader, logger):
        if not isinstance(loader, Loader):
            raise ValueError("Ingestion loader must be a Loader")
        if not isinstance(logger, Logger):
            raise ValueError("Ingestion logger must be a Logger")
        self.loader = loader
        self.logger = logger
        self.last_ingestion_stats = {
            "attempted": 0,
            "successful": 0,
            "failed": 0
        }
        self.last_ingestion_failures = []

    def ingest_directory(self, directory):
        if not isinstance(directory, str) or not directory:
            self.logger.error("Ingestion directory must be a non-empty string")
            raise ValueError("Ingestion directory must be a non-empty string")
        if not os.path.isdir(directory):
            self.logger.error(f"Ingestion directory not found: {directory}")
            raise FileNotFoundError(f"Ingestion directory not found: {directory}")

        self.logger.info(f"Starting ingestion: {directory}")
        paths = self.loader.find_files(directory)
        documents = self.loader.load_many(paths)
        self.last_ingestion_stats = self.loader.get_batch_stats()
        self.last_ingestion_failures = []
        for path in paths:
            try:
                self.loader.load(path)
            except Exception as e:
                self.last_ingestion_failures.append({
                    "path": path,
                    "error": str(e)
                })
        self.logger.info(
            f"Ingestion complete: {len(documents)}/{len(paths)} documents loaded"
        )
        return documents

    def get_ingestion_stats(self):
        return self.last_ingestion_stats.copy()

    def get_ingestion_failures(self):
        return self.last_ingestion_failures.copy()