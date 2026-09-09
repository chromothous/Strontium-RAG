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

    def ingest_directory(self, directory):
        self.logger.info(f"Starting ingestion: {directory}")
        paths = self.loader.find_files(directory)
        documents = self.loader.load_many(paths)
        self.logger.info(
            f"Ingestion complete: {len(documents)}/{len(paths)} documents loaded"
        )
        return documents