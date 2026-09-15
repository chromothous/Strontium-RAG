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
                "failure_type": None,
                "error": None,
                "traceback": None
            }
        except AssertionError as e:
            self.failure += 1
            result = {
                "name": name,
                "success": False,
                "failure_type": "assertion",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        except Exception as e:
            self.failure += 1
            result = {
                "name": name,
                "success": False,
                "failure_type": "exception",
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
            raise ValueError(
                "Test discovery directory must be a string"
            )
        if not directory.strip():
            raise ValueError(
                "Test discovery directory cannot be empty"
            )
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
            f"Test discovery completed: "
            f"{len(discovered)} tests discovered"
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

    def execute(self, tests=None):
        if tests is None:
            tests = self._registered_tests
        if not isinstance(tests, (list, tuple)):
            raise ValueError(
                "Tests to execute must be a list or tuple"
            )
        execution_results = []
        for test in tests:
            if not isinstance(test, dict):
                raise ValueError(
                    "Each test to execute must be a dictionary"
                )
            if "name" not in test:
                raise ValueError(
                    "Test to execute is missing name"
                )
            if "function" not in test:
                raise ValueError(
                    "Test to execute is missing function"
                )
            name = test["name"]
            test_function = test["function"]
            if not isinstance(name, str):
                raise ValueError(
                    "Test execution name must be a string"
                )
            if not callable(test_function):
                raise ValueError(
                    "Test execution function must be callable"
                )
            execution_results.append(
                self.run_test(
                    name,
                    test_function
                )
            )
        return execution_results

    def execute_discovered(self, directory):
        self.register_discovered(directory)
        return self.execute()

    def run_regression_suite(self, suite_path):
        if not isinstance(suite_path, str):
            raise ValueError(
                "Regression suite path must be a string"
            )
        if not suite_path.strip():
            raise ValueError(
                "Regression suite path cannot be empty"
            )
        if not os.path.isfile(suite_path):
            raise ValueError(
                "Regression suite file does not exist"
            )
        module_name = (
            f"regression_{os.path.splitext(os.path.basename(suite_path))[0]}"
        )
        spec = importlib.util.spec_from_file_location(
            module_name,
            suite_path
        )
        if spec is None or spec.loader is None:
            raise ValueError(
                "Regression suite could not be loaded"
            )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if not hasattr(module, "full_test"):
            raise ValueError(
                "Regression suite must provide a full_test function"
            )
        full_test = module.full_test
        if not callable(full_test):
            raise ValueError(
                "Regression suite full_test must be callable"
            )
        return self.run_test(
            "cumulative_regression_suite",
            full_test
        )

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