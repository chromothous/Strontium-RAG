import os
import sys
from pathlib import Path


class PythonRuntime:
    def __init__(self):
        self.executable = str(Path(sys.executable).resolve())
        self.version = sys.version_info
        self.project_root = Path(__file__).resolve().parent.parent
        self.working_directory = Path.cwd().resolve()
        self.module_path = self._get_module_path()

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
            raise RuntimeError("Python project root is not valid.")
        project_root = str(self.project_root)
        if project_root not in self._get_module_path():
            sys.path.insert(0, project_root)
        os.chdir(project_root)
        self.working_directory = Path.cwd().resolve()
        self.module_path = self._get_module_path()
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
        }

    def validate(self):
        if not self.is_available():
            raise RuntimeError("Python 3 runtime is not available.")
        if not self.has_predictable_working_directory():
            raise RuntimeError("Python project root is not valid.")
        if not self.has_import_path():
            raise RuntimeError("Python project root is missing from the import path.")
        return True