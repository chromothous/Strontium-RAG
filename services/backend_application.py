from classes.logger import Logger
from configuration.backend_architecture import BackendArchitecture


class BackendApplication:
    def __init__(self, logger):
        if not isinstance(logger, Logger):
            raise ValueError("Backend application logger must be a Logger")
        self.logger = logger
        self.architecture = BackendArchitecture(logger)
        self.initialized = False
        self.logger.info("Backend application created.")

    def initialize(self):
        if self.initialized:
            self.logger.info("Backend application is already initialized.")
            return
        if not self.architecture.is_defined():
            self.logger.error("Backend architecture is not defined.")
            raise RuntimeError("Backend architecture is not defined.")
        self.initialized = True
        self.logger.info("Backend application initialized successfully.")

    def is_initialized(self):
        return self.initialized

    def get_architecture(self):
        return self.architecture.get_definition()