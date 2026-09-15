import importlib.util
import inspect
import os
import traceback


class TestRunner:
    def __init__(self):
        self.tests = 0
        self.success = 0
        self.failure = 0
        self.results = []
        self._registered_tests = []

    def register(self, name, test_function):
        if not isinstance(name, str):
            raise ValueError("Test name must be a string")
        if not name.strip():
            raise ValueError("Test name cannot be empty")
        if not callable(test_function):
            raise ValueError("Test function must be callable")
        self._registered_tests.append(
            {
                "name": name,
                "function": test_function
            }
        )

    def get_registered_tests(self):
        return list(self._registered_tests)

    def run_test(self, name, test_function):
        self.tests += 1
        try:
            test_function()
            self.success += 1
            result = {
                "name": name,
                "success": True,
                "error": None
            }
        except Exception as e:
            self.failure += 1
            result = {
                "name": name,
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        self.results.append(result)
        return result

    def run_registered(self):
        for test in self._registered_tests:
            self.run_test(
                test["name"],
                test["function"]
            )
        return self.get_results()

    def discover(self, directory):
        if not isinstance(directory, str):
            raise ValueError("Test discovery directory must be a string")
        if not directory.strip():
            raise ValueError("Test discovery directory cannot be empty")
        if not os.path.isdir(directory):
            raise ValueError(
                "Test discovery directory does not exist"
            )
        discovered = []
        for filename in sorted(os.listdir(directory)):
            if not filename.startswith("test_"):
                continue
            if not filename.endswith(".py"):
                continue
            module_path = os.path.join(directory, filename)
            module_name = (
                f"discovered_{os.path.splitext(filename)[0]}"
            )
            spec = importlib.util.spec_from_file_location(
                module_name,
                module_path
            )
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for name, test_function in inspect.getmembers(
                module,
                inspect.isfunction
            ):
                if name.startswith("test_"):
                    discovered.append(
                        {
                            "name": f"{filename}:{name}",
                            "function": test_function
                        }
                    )
        self.logger_info(
            f"Test discovery completed: {len(discovered)} tests discovered"
        )
        return discovered

    def register_discovered(self, directory):
        discovered = self.discover(directory)
        for test in discovered:
            self.register(
                test["name"],
                test["function"]
            )
        return discovered

    def logger_info(self, message):
        return message

    def get_results(self):
        return {
            "tests": self.tests,
            "success": self.success,
            "failure": self.failure,
            "results": list(self.results)
        }

    def reset(self):
        self.tests = 0
        self.success = 0
        self.failure = 0
        self.results = []