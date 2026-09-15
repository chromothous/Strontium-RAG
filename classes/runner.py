import importlib.util
import inspect
import os
import traceback

from classes.logger import Logger


class TestRunner:
    def __init__(self, logger=None):
        if logger is None:
            logger = Logger()
        if not isinstance(logger, Logger):
            raise ValueError("Test runner logger must be a Logger")
        self.logger = logger
        self.tests = 0
        self.success = 0
        self.failure = 0
        self.results = []
        self._registered_tests = []
        self._test_state = {}
        self._fixtures = {}
        self._integration_tests = {}
        self.logger.info("Test runner initialized")

    def register(self, name, test_function):
        if not isinstance(name, str):
            self.logger.error("Test name must be a string")
            raise ValueError("Test name must be a string")
        if not name.strip():
            self.logger.error("Test name cannot be empty")
            raise ValueError("Test name cannot be empty")
        if not callable(test_function):
            self.logger.error("Test function must be callable")
            raise ValueError("Test function must be callable")
        self._registered_tests.append(
            {
                "name": name,
                "function": test_function
            }
        )
        self.logger.info(
            f"Test registered: {name}"
        )

    def get_registered_tests(self):
        return list(self._registered_tests)

    def get_test_state(self):
        return dict(self._test_state)

    def set_test_state(self, key, value):
        if not isinstance(key, str):
            self.logger.error("Test state key must be a string")
            raise ValueError("Test state key must be a string")
        if not key.strip():
            self.logger.error("Test state key cannot be empty")
            raise ValueError("Test state key cannot be empty")
        self._test_state[key] = value
        self.logger.info(
            f"Test state updated: {key}"
        )

    def clear_test_state(self):
        self._test_state = {}
        self.logger.info("Test state cleared")

    def register_fixture(self, name, fixture_function):
        if not isinstance(name, str):
            self.logger.error("Fixture name must be a string")
            raise ValueError("Fixture name must be a string")
        if not name.strip():
            self.logger.error("Fixture name cannot be empty")
            raise ValueError("Fixture name cannot be empty")
        if not callable(fixture_function):
            self.logger.error("Fixture function must be callable")
            raise ValueError("Fixture function must be callable")
        self._fixtures[name] = fixture_function
        self.logger.info(
            f"Test fixture registered: {name}"
        )

    def get_registered_fixtures(self):
        return dict(self._fixtures)

    def get_fixture(self, name):
        if not isinstance(name, str):
            self.logger.error("Fixture name must be a string")
            raise ValueError("Fixture name must be a string")
        if name not in self._fixtures:
            self.logger.error(
                f"Fixture not found: {name}"
            )
            raise ValueError(
                f"Fixture '{name}' is not registered"
            )
        self.logger.info(
            f"Test fixture requested: {name}"
        )
        return self._fixtures[name]()

    def load_fixtures(self, fixture_definitions):
        if not isinstance(fixture_definitions, (list, tuple)):
            self.logger.error(
                "Fixture definitions must be a list or tuple"
            )
            raise ValueError(
                "Fixture definitions must be a list or tuple"
            )
        for fixture in fixture_definitions:
            if not isinstance(fixture, dict):
                self.logger.error(
                    "Fixture definition must be a dictionary"
                )
                raise ValueError(
                    "Each fixture definition must be a dictionary"
                )
            if "name" not in fixture:
                self.logger.error(
                    "Fixture definition is missing name"
                )
                raise ValueError(
                    "Fixture definition is missing name"
                )
            if "function" not in fixture:
                self.logger.error(
                    "Fixture definition is missing function"
                )
                raise ValueError(
                    "Fixture definition is missing function"
                )
            self.register_fixture(
                fixture["name"],
                fixture["function"]
            )
        return self.get_registered_fixtures()

    def register_integration_test(self, name, test_function):
        if not isinstance(name, str):
            self.logger.error(
                "Integration test name must be a string"
            )
            raise ValueError(
                "Integration test name must be a string"
            )
        if not name.strip():
            self.logger.error(
                "Integration test name cannot be empty"
            )
            raise ValueError(
                "Integration test name cannot be empty"
            )
        if not callable(test_function):
            self.logger.error(
                "Integration test function must be callable"
            )
            raise ValueError(
                "Integration test function must be callable"
            )
        self._integration_tests[name] = test_function
        self.logger.info(
            f"Integration test registered: {name}"
        )

    def get_registered_integration_tests(self):
        return dict(self._integration_tests)

    def _execute_function(self, test_function):
        parameters = inspect.signature(test_function).parameters
        if len(parameters) == 0:
            return test_function()
        if len(parameters) == 1:
            return test_function(self.get_test_state())
        raise ValueError(
            "Test function must accept zero or one parameter"
        )

    def run_test(self, name, test_function):
        self.tests += 1
        self.logger.info(
            f"Test execution started: {name}"
        )
        try:
            self._execute_function(test_function)
            self.success += 1
            result = {
                "name": name,
                "success": True,
                "failure_type": None,
                "error": None,
                "traceback": None
            }
            self.logger.info(
                f"Test execution succeeded: {name}"
            )
        except AssertionError as e:
            self.failure += 1
            result = {
                "name": name,
                "success": False,
                "failure_type": "assertion",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            self.logger.error(
                f"Test assertion failure: {name} - {e}"
            )
        except Exception as e:
            self.failure += 1
            result = {
                "name": name,
                "success": False,
                "failure_type": "exception",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            self.logger.error(
                f"Test exception: {name} - {e}"
            )
        self.results.append(result)
        return result

    def run_isolated_test(self, name, test_function):
        self.logger.info(
            f"Isolated test execution started: {name}"
        )
        self.clear_test_state()
        result = self.run_test(
            name,
            test_function
        )
        self.clear_test_state()
        self.logger.info(
            f"Isolated test execution completed: {name}"
        )
        return result

    def run_integration_test(self, name, test_function):
        self.logger.info(
            f"Integration test execution started: {name}"
        )
        self.clear_test_state()
        result = self.run_test(
            f"integration:{name}",
            test_function
        )
        self.clear_test_state()
        self.logger.info(
            f"Integration test execution completed: {name}"
        )
        return result

    def run_registered(self):
        self.logger.info(
            f"Registered test execution started: "
            f"{len(self._registered_tests)} tests"
        )
        for test in self._registered_tests:
            self.run_test(
                test["name"],
                test["function"]
            )
        self.logger.info(
            "Registered test execution completed"
        )
        return self.get_results()

    def run_registered_integration(self):
        self.logger.info(
            f"Registered integration test execution started: "
            f"{len(self._integration_tests)} tests"
        )
        for name, test_function in self._integration_tests.items():
            self.run_integration_test(
                name,
                test_function
            )
        self.logger.info(
            "Registered integration test execution completed"
        )
        return self.get_results()

    def discover(self, directory):
        if not isinstance(directory, str):
            self.logger.error(
                "Test discovery directory must be a string"
            )
            raise ValueError(
                "Test discovery directory must be a string"
            )
        if not directory.strip():
            self.logger.error(
                "Test discovery directory cannot be empty"
            )
            raise ValueError(
                "Test discovery directory cannot be empty"
            )
        if not os.path.isdir(directory):
            self.logger.error(
                "Test discovery directory does not exist"
            )
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
                self.logger.warning(
                    f"Test module could not be loaded: {filename}"
                )
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
        self.logger.info(
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
        self.logger.info(
            f"Discovered tests registered: {len(discovered)}"
        )
        return discovered

    def execute(self, tests=None):
        if tests is None:
            tests = self._registered_tests
        if not isinstance(tests, (list, tuple)):
            self.logger.error(
                "Tests to execute must be a list or tuple"
            )
            raise ValueError(
                "Tests to execute must be a list or tuple"
            )
        execution_results = []
        self.logger.info(
            f"Test execution requested: {len(tests)} tests"
        )
        for test in tests:
            if not isinstance(test, dict):
                self.logger.error(
                    "Each test to execute must be a dictionary"
                )
                raise ValueError(
                    "Each test to execute must be a dictionary"
                )
            if "name" not in test:
                self.logger.error(
                    "Test to execute is missing name"
                )
                raise ValueError(
                    "Test to execute is missing name"
                )
            if "function" not in test:
                self.logger.error(
                    "Test to execute is missing function"
                )
                raise ValueError(
                    "Test to execute is missing function"
                )
            name = test["name"]
            test_function = test["function"]
            if not isinstance(name, str):
                self.logger.error(
                    "Test execution name must be a string"
                )
                raise ValueError(
                    "Test execution name must be a string"
                )
            if not callable(test_function):
                self.logger.error(
                    "Test execution function must be callable"
                )
                raise ValueError(
                    "Test execution function must be callable"
                )
            execution_results.append(
                self.run_test(
                    name,
                    test_function
                )
            )
        self.logger.info(
            "Test execution completed"
        )
        return execution_results

    def execute_isolated(self, tests=None):
        if tests is None:
            tests = self._registered_tests
        if not isinstance(tests, (list, tuple)):
            self.logger.error(
                "Isolated tests to execute must be a list or tuple"
            )
            raise ValueError(
                "Isolated tests to execute must be a list or tuple"
            )
        execution_results = []
        self.logger.info(
            f"Isolated test execution requested: {len(tests)} tests"
        )
        for test in tests:
            if not isinstance(test, dict):
                self.logger.error(
                    "Each isolated test must be a dictionary"
                )
                raise ValueError(
                    "Each isolated test must be a dictionary"
                )
            if "name" not in test:
                self.logger.error(
                    "Isolated test is missing name"
                )
                raise ValueError(
                    "Isolated test is missing name"
                )
            if "function" not in test:
                self.logger.error(
                    "Isolated test is missing function"
                )
                raise ValueError(
                    "Isolated test is missing function"
                )
            name = test["name"]
            test_function = test["function"]
            if not isinstance(name, str):
                self.logger.error(
                    "Isolated test name must be a string"
                )
                raise ValueError(
                    "Isolated test name must be a string"
                )
            if not callable(test_function):
                self.logger.error(
                    "Isolated test function must be callable"
                )
                raise ValueError(
                    "Isolated test function must be callable"
                )
            execution_results.append(
                self.run_isolated_test(
                    name,
                    test_function
                )
            )
        self.logger.info(
            "Isolated test execution completed"
        )
        return execution_results

    def execute_integration(self, tests=None):
        if tests is None:
            tests = self._integration_tests
        if isinstance(tests, dict):
            tests = list(tests.items())
        if not isinstance(tests, (list, tuple)):
            self.logger.error(
                "Integration tests to execute must be a list, tuple, or dictionary"
            )
            raise ValueError(
                "Integration tests to execute must be a list, tuple, or dictionary"
            )
        execution_results = []
        self.logger.info(
            f"Integration test execution requested: {len(tests)} tests"
        )
        for test in tests:
            if isinstance(test, tuple):
                if len(test) != 2:
                    self.logger.error(
                        "Integration test tuple must contain a name and function"
                    )
                    raise ValueError(
                        "Integration test tuple must contain a name and function"
                    )
                name, test_function = test
            elif isinstance(test, dict):
                if "name" not in test:
                    self.logger.error(
                        "Integration test is missing name"
                    )
                    raise ValueError(
                        "Integration test is missing name"
                    )
                if "function" not in test:
                    self.logger.error(
                        "Integration test is missing function"
                    )
                    raise ValueError(
                        "Integration test is missing function"
                    )
                name = test["name"]
                test_function = test["function"]
            else:
                self.logger.error(
                    "Integration test must be a tuple or dictionary"
                )
                raise ValueError(
                    "Integration test must be a tuple or dictionary"
                )
            execution_results.append(
                self.run_integration_test(
                    name,
                    test_function
                )
            )
        self.logger.info(
            "Integration test execution completed"
        )
        return execution_results

    def execute_discovered(self, directory):
        self.logger.info(
            f"Discovered test execution requested: {directory}"
        )
        self.register_discovered(directory)
        return self.execute()

    def run_regression_suite(self, suite_path):
        if not isinstance(suite_path, str):
            self.logger.error(
                "Regression suite path must be a string"
            )
            raise ValueError(
                "Regression suite path must be a string"
            )
        if not suite_path.strip():
            self.logger.error(
                "Regression suite path cannot be empty"
            )
            raise ValueError(
                "Regression suite path cannot be empty"
            )
        if not os.path.isfile(suite_path):
            self.logger.error(
                "Regression suite file does not exist"
            )
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
            self.logger.error(
                "Regression suite could not be loaded"
            )
            raise ValueError(
                "Regression suite could not be loaded"
            )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if not hasattr(module, "full_test"):
            self.logger.error(
                "Regression suite must provide a full_test function"
            )
            raise ValueError(
                "Regression suite must provide a full_test function"
            )
        full_test = module.full_test
        if not callable(full_test):
            self.logger.error(
                "Regression suite full_test must be callable"
            )
            raise ValueError(
                "Regression suite full_test must be callable"
            )
        self.logger.info(
            "Cumulative regression suite execution started"
        )
        return self.run_test(
            "cumulative_regression_suite",
            full_test
        )

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
        self._test_state = {}
        self.logger.info("Test runner state reset")