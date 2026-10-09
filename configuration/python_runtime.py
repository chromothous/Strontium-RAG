import importlib.util
import os
import sys
from pathlib import Path
from classes.logger import Logger
from classes.error_handler import ErrorHandler
from configuration.environment_configuration import EnvironmentConfiguration


class PythonRuntime:
    def __init__(self, logger, required_dependencies=(), error_handler=None):
        if not isinstance(logger, Logger):
            raise ValueError("Python runtime logger must be a Logger")
        self.logger = logger
        if error_handler is None:
            self.error_handler = ErrorHandler(logger)
        elif not isinstance(error_handler, ErrorHandler):
            self.logger.error("Python runtime error handler must be an ErrorHandler.")
            raise ValueError("Python runtime error handler must be an ErrorHandler")
        else:
            self.error_handler = error_handler
        if not isinstance(required_dependencies, (list, tuple)):
            self._record_expected_failure("Required Python dependencies must be a list or tuple.", "configure_dependencies")
            raise ValueError("Python runtime dependencies must be a list or tuple")
        for dependency in required_dependencies:
            if not isinstance(dependency, str) or not dependency.strip():
                self._record_expected_failure("Python runtime dependency names must be non-empty strings.", "configure_dependencies")
                raise ValueError("Python runtime dependency names must be non-empty strings")
        self.required_dependencies = tuple(dependency.strip() for dependency in required_dependencies)
        self.executable = str(Path(sys.executable).resolve())
        self.version = sys.version_info
        self.project_root = Path(__file__).resolve().parent.parent
        self.working_directory = Path.cwd().resolve()
        self.module_path = self._get_module_path()
        self.logger.info("Python runtime inspection initialized.")

    def _record_expected_failure(self, message, operation, details=None):
        return self.error_handler.handle_expected(
            message,
            category="system",
            component="python_runtime",
            operation=operation,
            details=details or {},
            recoverable=False,
            user_message="The Python runtime could not complete the requested operation."
        )

    def _record_unexpected_failure(self, exception, operation):
        return self.error_handler.handle_unexpected(
            exception,
            component="python_runtime",
            operation=operation,
            details={"exception_type": type(exception).__name__}
        )

    def _get_module_path(self):
        return tuple(
            str(Path(path or os.getcwd()).resolve())
            for path in sys.path
        )

    def is_available(self):
        return bool(self.executable) and self.version.major == 3

    def get_project_root(self):
        return str(self.project_root)

    def has_predictable_working_directory(self):
        return (
            self.project_root.is_dir()
            and (self.project_root / "main.py").is_file()
        )

    def has_import_path(self):
        return str(self.project_root) in self._get_module_path()

    def activate_project_root(self):
        if not self.has_predictable_working_directory():
            message = "Python project root is not valid."
            self._record_expected_failure(message, "activate_project_root")
            raise RuntimeError(message)
        project_root = str(self.project_root)
        try:
            os.chdir(project_root)
        except OSError as error:
            self._record_unexpected_failure(error, "activate_project_root")
            raise RuntimeError("Python project root activation failed.") from error
        if project_root not in self._get_module_path():
            sys.path.insert(0, project_root)
        self.working_directory = Path.cwd().resolve()
        self.module_path = self._get_module_path()
        self.logger.info("Python project root activated successfully.")
        return True

    def get_version(self):
        return {
            "major": self.version.major,
            "minor": self.version.minor,
            "micro": self.version.micro,
        }

    def get_definition(self):
        return {
            "executable": self.executable,
            "version": self.get_version(),
            "project_root": self.get_project_root(),
            "working_directory": str(self.working_directory),
            "module_path": self.module_path,
            "required_dependencies": self.required_dependencies,
        }

    def validate_dependencies(self):
        missing_dependencies = []
        for dependency in self.required_dependencies:
            try:
                specification = importlib.util.find_spec(dependency)
            except (ImportError, ModuleNotFoundError, ValueError):
                specification = None
            if specification is None:
                missing_dependencies.append(dependency)
        if missing_dependencies:
            message = (
                "Required Python dependency modules are unavailable: "
                + ", ".join(missing_dependencies)
            )
            self._record_expected_failure(
                message,
                "validate_dependencies",
                {"missing_dependencies": tuple(missing_dependencies)}
            )
            raise RuntimeError(message)
        self.logger.info(
            f"Python runtime dependency validation passed: "
            f"{len(self.required_dependencies)} dependencies checked."
        )
        return True

    def validate_environment(self, environment_configuration):
        if not isinstance(environment_configuration, EnvironmentConfiguration):
            message = "Python runtime requires an EnvironmentConfiguration instance"
            self._record_expected_failure(message, "validate_environment")
            raise ValueError(message)
        try:
            environment_configuration.validate_required()
        except RuntimeError as error:
            self._record_expected_failure(
                str(error),
                "validate_environment",
                {"failure_type": type(error).__name__}
            )
            raise
        self.logger.info("Python runtime environment validation passed.")
        return True

    def validate(self, environment_configuration=None):
        if not self.is_available():
            message = "Python 3 runtime is not available."
            self._record_expected_failure(message, "validate_runtime")
            raise RuntimeError(message)
        if not self.has_predictable_working_directory():
            message = "Python project root is not valid."
            self._record_expected_failure(message, "validate_working_directory")
            raise RuntimeError(message)
        if not self.has_import_path():
            message = "Python project root is missing from the import path."
            self._record_expected_failure(message, "validate_import_path")
            raise RuntimeError(message)
        self.validate_dependencies()
        if environment_configuration is not None:
            self.validate_environment(environment_configuration)
        self.logger.info("Python runtime validation passed.")
        return True