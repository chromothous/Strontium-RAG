import importlib.util
import os
import sys
from pathlib import Path
from classes.logger import Logger


class PythonRuntime:
    def __init__(self, logger, required_dependencies=()):
        if not isinstance(logger, Logger):
            raise ValueError("Python runtime logger must be a Logger")
        if not isinstance(required_dependencies, (list, tuple)):
            logger.error("Python runtime dependencies must be a list or tuple.")
            raise ValueError("Python runtime dependencies must be a list or tuple")
        for dependency in required_dependencies:
            if not isinstance(dependency, str) or not dependency.strip():
                logger.error("Python runtime dependency names must be non-empty strings.")
                raise ValueError("Python runtime dependency names must be non-empty strings")
        self.logger = logger
        self.required_dependencies = tuple(dependency.strip() for dependency in required_dependencies)
        self.executable = str(Path(sys.executable).resolve())
        self.version = sys.version_info
        self.project_root = Path(__file__).resolve().parent.parent
        self.working_directory = Path.cwd().resolve()
        self.module_path = self._get_module_path()
        self.logger.info("Python runtime inspection initialized.")

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
            self.logger.error("Python project root is not valid.")
            raise RuntimeError("Python project root is not valid.")
        project_root = str(self.project_root)
        try:
            os.chdir(project_root)
        except OSError as e:
            self.logger.error(f"Python project root activation failed: {e}")
            raise RuntimeError("Python project root activation failed.") from e
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
            self.logger.error(message)
            raise RuntimeError(message)
        self.logger.info(
            f"Python runtime dependency validation passed: "
            f"{len(self.required_dependencies)} dependencies checked."
        )
        return True

    def validate(self):
        if not self.is_available():
            self.logger.error("Python 3 runtime is not available.")
            raise RuntimeError("Python 3 runtime is not available.")
        if not self.has_predictable_working_directory():
            self.logger.error("Python project root is not valid.")
            raise RuntimeError("Python project root is not valid.")
        if not self.has_import_path():
            self.logger.error("Python project root is missing from the import path.")
            raise RuntimeError("Python project root is missing from the import path.")
        self.validate_dependencies()
        self.logger.info("Python runtime validation passed.")
        return True