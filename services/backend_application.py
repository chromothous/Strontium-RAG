from classes.logger import Logger
from configuration.backend_architecture import BackendArchitecture


class BackendApplication:
    def __init__(self, logger):
        if not isinstance(logger, Logger):
            raise ValueError("Backend application logger must be a Logger")
        self.logger = logger
        self.architecture = BackendArchitecture(logger)
        self.initialized = False
        self.shutting_down = False
        self.shutdown_complete = False
        self.logger.info("Backend application created.")

    def initialize(self):
        if self.shutting_down:
            self.logger.error("Backend application cannot initialize during shutdown.")
            raise RuntimeError("Backend application cannot initialize during shutdown.")
        if self.initialized and not self.shutdown_complete:
            self.logger.info("Backend application is already initialized.")
            return True
        if not self.architecture.is_defined():
            self.logger.error("Backend architecture is not defined.")
            raise RuntimeError("Backend architecture is not defined.")
        self.initialized = True
        self.shutting_down = False
        self.shutdown_complete = False
        self.logger.info("Backend application initialized successfully.")
        return True

    def shutdown(self):
        if self.shutdown_complete:
            self.logger.info("Backend application is already shut down.")
            return True
        self.shutting_down = True
        self.logger.info("Backend application shutdown requested.")
        try:
            if self.initialized:
                self.logger.info("Stopping initialized backend application.")
            else:
                self.logger.warning("Shutdown requested before initialization completed.")
            self.initialized = False
            self.shutdown_complete = True
            self.logger.info("Backend application shutdown completed.")
            return True
        except Exception as error:
            self.logger.error(f"Backend application shutdown failed: {error}")
            raise RuntimeError("Backend application shutdown failed.") from error
        finally:
            self.shutting_down = False

    def is_initialized(self):
        return self.initialized

    def is_shutting_down(self):
        return self.shutting_down

    def is_shutdown(self):
        return self.shutdown_complete

    def get_lifecycle_state(self):
        return {
            "initialized": self.initialized,
            "shutting_down": self.shutting_down,
            "shutdown_complete": self.shutdown_complete,
        }

    def get_architecture(self):
        return self.architecture.get_definition()