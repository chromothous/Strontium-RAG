from classes.logger import Logger
from classes.error_handler import ErrorHandler
from configuration.backend_architecture import BackendArchitecture
from configuration.environment_configuration import EnvironmentConfiguration
from configuration.python_runtime import PythonRuntime
from configuration.startup_configuration import StartupConfiguration


class BackendApplication:
    def __init__(
        self,
        logger,
        required_dependencies=(),
        environment_configuration=None,
        startup_configuration=None,
    ):
        if not isinstance(logger, Logger):
            raise ValueError("Backend application logger must be a Logger")
        self.logger = logger
        self.error_handler = ErrorHandler(logger)
        self.architecture = BackendArchitecture(logger)
        if environment_configuration is not None:
            if not isinstance(environment_configuration, EnvironmentConfiguration):
                self.logger.error("Backend application environment configuration must be an EnvironmentConfiguration.")
                raise ValueError("Backend application environment configuration must be an EnvironmentConfiguration")
            if environment_configuration.logger is not logger:
                raise ValueError("Backend application components must share the same Logger instance")
        if startup_configuration is None:
            startup_configuration = StartupConfiguration(logger)
        elif not isinstance(startup_configuration, StartupConfiguration):
            self.logger.error("Backend application startup configuration must be a StartupConfiguration.")
            raise ValueError("Backend application startup configuration must be a StartupConfiguration")
        if startup_configuration.logger is not logger:
            raise ValueError("Backend application components must share the same Logger instance")
        self.environment_configuration = environment_configuration
        self.startup_configuration = startup_configuration
        self.runtime = PythonRuntime(
            logger,
            required_dependencies=required_dependencies,
            error_handler=self.error_handler,
        )
        self.initialized = False
        self.shutting_down = False
        self.shutdown_complete = False
        self.runtime_validated = False
        self.logger.info("Backend application created.")

    def _record_startup_failure(self, error, previous_diagnostic_count):
        if len(self.error_handler.get_diagnostics()) != previous_diagnostic_count:
            return
        details = {"exception_type": type(error).__name__}
        if isinstance(error, (ValueError, RuntimeError)):
            self.error_handler.handle_expected(
                str(error),
                category="system",
                component="backend_application",
                operation="initialize",
                details=details,
                cause=error,
                recoverable=False,
            )
        else:
            self.error_handler.handle_unexpected(
                error,
                component="backend_application",
                operation="initialize",
                details=details,
            )

    def initialize(self):
        if self.shutting_down:
            self.logger.error("Backend application cannot initialize during shutdown.")
            raise RuntimeError("Backend application cannot initialize during shutdown.")
        if self.initialized and not self.shutdown_complete:
            self.logger.info("Backend application is already initialized.")
            return True
        previous_diagnostic_count = len(self.error_handler.get_diagnostics())
        self.logger.info("Backend application startup requested.")
        try:
            self.startup_configuration.validate()
            if not self.architecture.is_defined():
                raise RuntimeError("Backend architecture is not defined.")
            self.runtime.activate_project_root()
            self.runtime.validate(self.environment_configuration)
        except Exception as error:
            self.initialized = False
            self.runtime_validated = False
            self.shutdown_complete = False
            self.shutting_down = False
            self._record_startup_failure(error, previous_diagnostic_count)
            raise
        self.runtime_validated = True
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
            self.runtime_validated = False
            self.shutdown_complete = True
            self.logger.info("Backend application shutdown completed.")
            return True
        except Exception as error:
            self.error_handler.handle_unexpected(
                error,
                component="backend_application",
                operation="shutdown",
                details={"exception_type": type(error).__name__},
            )
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
            "runtime_validated": self.runtime_validated,
        }

    def get_architecture(self):
        return self.architecture.get_definition()