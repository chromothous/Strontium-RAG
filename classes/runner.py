import importlib.util
import inspect
import os
import trace
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
        self.skipped = 0
        self.results = []
        self._registered_tests = []
        self._test_state = {}
        self._fixtures = {}
        self._integration_tests = {}
        self._coverage_results = {}
        self._repeatability_results = {}
        self._regression_results = {}
        self._pipeline_results = {}
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
                "skipped": False,
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
                "skipped": False,
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
                "skipped": False,
                "failure_type": "exception",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            self.logger.error(
                f"Test exception: {name} - {e}"
            )
        self.results.append(result)
        return result

    def record_skipped(self, name, reason=None):
        if not isinstance(name, str):
            self.logger.error("Skipped test name must be a string")
            raise ValueError("Skipped test name must be a string")
        if not name.strip():
            self.logger.error("Skipped test name cannot be empty")
            raise ValueError("Skipped test name cannot be empty")
        if reason is not None and not isinstance(reason, str):
            self.logger.error("Skipped test reason must be a string or None")
            raise ValueError(
                "Skipped test reason must be a string or None"
            )
        self.skipped += 1
        result = {
            "name": name,
            "success": False,
            "skipped": True,
            "failure_type": None,
            "error": reason,
            "traceback": None
        }
        self.results.append(result)
        self.logger.warning(
            f"Test skipped: {name}"
        )
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

    def execute_selected(self, names):
        if not isinstance(names, (list, tuple, set)):
            self.logger.error(
                "Selected test names must be a list, tuple, or set"
            )
            raise ValueError(
                "Selected test names must be a list, tuple, or set"
            )
        if len(names) == 0:
            self.logger.error(
                "Selected test names cannot be empty"
            )
            raise ValueError(
                "Selected test names cannot be empty"
            )
        normalized_names = []
        for name in names:
            if not isinstance(name, str):
                self.logger.error(
                    "Selected test name must be a string"
                )
                raise ValueError(
                    "Selected test name must be a string"
                )
            if not name.strip():
                self.logger.error(
                    "Selected test name cannot be empty"
                )
                raise ValueError(
                    "Selected test name cannot be empty"
                )
            normalized_names.append(name)

        registered_by_name = {
            test["name"]: test
            for test in self._registered_tests
        }
        missing_names = [
            name
            for name in normalized_names
            if name not in registered_by_name
        ]
        if missing_names:
            self.logger.error(
                f"Selected tests were not registered: {missing_names}"
            )
            raise ValueError(
                f"Selected tests were not registered: {missing_names}"
            )

        selected_tests = [
            registered_by_name[name]
            for name in normalized_names
        ]
        self.logger.info(
            f"Selective test execution requested: "
            f"{len(selected_tests)} tests"
        )
        return self.execute(selected_tests)

    def execute_selected_isolated(self, names):
        if not isinstance(names, (list, tuple, set)):
            self.logger.error(
                "Selected isolated test names must be a list, tuple, or set"
            )
            raise ValueError(
                "Selected isolated test names must be a list, tuple, or set"
            )
        if len(names) == 0:
            self.logger.error(
                "Selected isolated test names cannot be empty"
            )
            raise ValueError(
                "Selected isolated test names cannot be empty"
            )
        normalized_names = []
        for name in names:
            if not isinstance(name, str):
                self.logger.error(
                    "Selected isolated test name must be a string"
                )
                raise ValueError(
                    "Selected isolated test name must be a string"
                )
            if not name.strip():
                self.logger.error(
                    "Selected isolated test name cannot be empty"
                )
                raise ValueError(
                    "Selected isolated test name cannot be empty"
                )
            normalized_names.append(name)

        registered_by_name = {
            test["name"]: test
            for test in self._registered_tests
        }
        missing_names = [
            name
            for name in normalized_names
            if name not in registered_by_name
        ]
        if missing_names:
            self.logger.error(
                f"Selected isolated tests were not registered: {missing_names}"
            )
            raise ValueError(
                f"Selected isolated tests were not registered: {missing_names}"
            )

        selected_tests = [
            registered_by_name[name]
            for name in normalized_names
        ]
        self.logger.info(
            f"Selective isolated test execution requested: "
            f"{len(selected_tests)} tests"
        )
        return self.execute_isolated(selected_tests)

    def execute_discovered_selected(self, directory, names):
        self.logger.info(
            f"Selective discovered test execution requested: {directory}"
        )
        self.register_discovered(directory)
        return self.execute_selected(names)

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

    def execute_full_regression(self, suite_path):
        if not isinstance(suite_path, str):
            self.logger.error(
                "Full regression suite path must be a string"
            )
            raise ValueError(
                "Full regression suite path must be a string"
            )
        if not suite_path.strip():
            self.logger.error(
                "Full regression suite path cannot be empty"
            )
            raise ValueError(
                "Full regression suite path cannot be empty"
            )
        if not os.path.isfile(suite_path):
            self.logger.error(
                "Full regression suite file does not exist"
            )
            raise ValueError(
                "Full regression suite file does not exist"
            )

        self.reset()
        self.clear_test_state()

        regression_result = self.run_regression_suite(
            suite_path
        )
        report = self.get_report()

        complete = (
            regression_result["success"] is True
            and report["failure"] == 0
            and report["skipped"] == 0
        )

        self._regression_results = {
            "suite_path": suite_path,
            "complete": complete,
            "regression_result": regression_result,
            "report": report
        }

        self.logger.info(
            f"Full automated regression execution completed: "
            f"complete={complete}"
        )
        return dict(self._regression_results)

    def get_full_regression(self):
        return dict(self._regression_results)

    def get_results(self):
        return {
            "tests": self.tests,
            "success": self.success,
            "failure": self.failure,
            "skipped": self.skipped,
            "results": list(self.results)
        }

    def get_report(self):
        failed_tests = []
        assertion_failures = []
        exception_failures = []
        skipped_tests = []
        isolated_failures = []
        integration_failures = []
        diagnostics = []

        for result in self.results:
            name = result["name"]
            if result.get("skipped") is True:
                skipped_tests.append(name)
                continue
            if result["success"] is False:
                failed_tests.append(name)
                failure_type = result.get("failure_type")
                if failure_type == "assertion":
                    assertion_failures.append(name)
                elif failure_type == "exception":
                    exception_failures.append(name)
                if result.get("error") is not None:
                    diagnostics.append(
                        {
                            "name": name,
                            "type": failure_type,
                            "error": result.get("error"),
                            "traceback": result.get("traceback")
                        }
                    )
                if name.startswith("isolated:"):
                    isolated_failures.append(name)
                if name.startswith("integration:"):
                    integration_failures.append(name)

        report = {
            "tests": self.tests,
            "success": self.success,
            "failure": self.failure,
            "skipped": self.skipped,
            "failed_tests": failed_tests,
            "assertion_failures": assertion_failures,
            "exception_failures": exception_failures,
            "isolated_failures": isolated_failures,
            "integration_failures": integration_failures,
            "diagnostics": diagnostics,
            "results": list(self.results)
        }
        self.logger.info(
            "Test report generated"
        )
        return report

    def start_coverage(self):
        self._coverage_results = {}
        self._coverage_tracer = trace.Trace(
            count=True,
            trace=False
        )
        self._coverage_tracer.runfunc(
            lambda: None
        )
        self.logger.info("Coverage analysis started")

    def _run_with_coverage(self, tests):
        tracer = trace.Trace(
            count=True,
            trace=False
        )

        def execute_tests():
            for test in tests:
                self.run_test(
                    test["name"],
                    test["function"]
                )

        tracer.runfunc(execute_tests)
        results = tracer.results()
        coverage_data = {}

        for (filename, lineno), count in results.counts.items():
            if filename not in coverage_data:
                coverage_data[filename] = {
                    "executed_lines": [],
                    "execution_counts": {}
                }
            coverage_data[filename]["executed_lines"].append(lineno)
            coverage_data[filename]["execution_counts"][lineno] = count

        for filename in coverage_data:
            coverage_data[filename]["executed_lines"].sort()

        self._coverage_results = coverage_data
        self.logger.info(
            "Coverage analysis completed"
        )
        return coverage_data

    def analyze_coverage(self, tests=None):
        if tests is None:
            tests = self._registered_tests
        if not isinstance(tests, (list, tuple)):
            self.logger.error(
                "Coverage tests must be a list or tuple"
            )
            raise ValueError(
                "Coverage tests must be a list or tuple"
            )
        for test in tests:
            if not isinstance(test, dict):
                self.logger.error(
                    "Each coverage test must be a dictionary"
                )
                raise ValueError(
                    "Each coverage test must be a dictionary"
                )
            if "name" not in test:
                self.logger.error(
                    "Coverage test is missing name"
                )
                raise ValueError(
                    "Coverage test is missing name"
                )
            if "function" not in test:
                self.logger.error(
                    "Coverage test is missing function"
                )
                raise ValueError(
                    "Coverage test is missing function"
                )
            if not isinstance(test["name"], str):
                self.logger.error(
                    "Coverage test name must be a string"
                )
                raise ValueError(
                    "Coverage test name must be a string"
                )
            if not callable(test["function"]):
                self.logger.error(
                    "Coverage test function must be callable"
                )
                raise ValueError(
                    "Coverage test function must be callable"
                )

        self.reset()
        coverage_data = self._run_with_coverage(
            list(tests)
        )

        report = {
            "files": len(coverage_data),
            "coverage": dict(coverage_data),
            "tests": self.tests,
            "success": self.success,
            "failure": self.failure,
            "skipped": self.skipped
        }
        self.logger.info(
            "Coverage report generated"
        )
        return report

    def get_coverage(self):
        return {
            "files": len(self._coverage_results),
            "coverage": dict(self._coverage_results)
        }

    def _validate_repeatability_tests(self, tests):
        if not isinstance(tests, (list, tuple)):
            self.logger.error(
                "Repeatability tests must be a list or tuple"
            )
            raise ValueError(
                "Repeatability tests must be a list or tuple"
            )
        for test in tests:
            if not isinstance(test, dict):
                self.logger.error(
                    "Each repeatability test must be a dictionary"
                )
                raise ValueError(
                    "Each repeatability test must be a dictionary"
                )
            if "name" not in test:
                self.logger.error(
                    "Repeatability test is missing name"
                )
                raise ValueError(
                    "Repeatability test is missing name"
                )
            if "function" not in test:
                self.logger.error(
                    "Repeatability test is missing function"
                )
                raise ValueError(
                    "Repeatability test is missing function"
                )
            if not isinstance(test["name"], str):
                self.logger.error(
                    "Repeatability test name must be a string"
                )
                raise ValueError(
                    "Repeatability test name must be a string"
                )
            if not callable(test["function"]):
                self.logger.error(
                    "Repeatability test function must be callable"
                )
                raise ValueError(
                    "Repeatability test function must be callable"
                )

    def _result_signature(self, result):
        return (
            result["name"],
            result["success"],
            result.get("skipped", False),
            result.get("failure_type"),
            result.get("error")
        )

    def _execute_repeatability_run(self, tests):
        self.reset()
        self.clear_test_state()
        results = self.execute(
            list(tests)
        )
        final_state = self.get_test_state()
        return {
            "results": [
                self._result_signature(result)
                for result in results
            ],
            "state": dict(final_state),
            "tests": self.tests,
            "success": self.success,
            "failure": self.failure,
            "skipped": self.skipped
        }

    def analyze_repeatability(self, tests=None, repetitions=2):
        if tests is None:
            tests = self._registered_tests
        self._validate_repeatability_tests(tests)
        if not isinstance(repetitions, int):
            self.logger.error(
                "Repeatability repetitions must be an integer"
            )
            raise ValueError(
                "Repeatability repetitions must be an integer"
            )
        if repetitions < 2:
            self.logger.error(
                "Repeatability repetitions must be at least two"
            )
            raise ValueError(
                "Repeatability repetitions must be at least two"
            )

        runs = []
        for index in range(repetitions):
            self.logger.info(
                f"Repeatability run started: {index + 1}"
            )
            runs.append(
                self._execute_repeatability_run(
                    list(tests)
                )
            )
            self.logger.info(
                f"Repeatability run completed: {index + 1}"
            )

        baseline = runs[0]
        inconsistent_runs = []
        state_leakage_detected = False

        for index, current_run in enumerate(runs[1:], start=2):
            if current_run != baseline:
                inconsistent_runs.append(index)

        for run in runs:
            if run["state"] != {}:
                state_leakage_detected = True

        deterministic = (
            len(inconsistent_runs) == 0
            and not state_leakage_detected
        )

        self._repeatability_results = {
            "repetitions": repetitions,
            "deterministic": deterministic,
            "inconsistent_runs": inconsistent_runs,
            "state_leakage_detected": state_leakage_detected,
            "runs": runs
        }

        self.logger.info(
            f"Repeatability analysis completed: deterministic={deterministic}"
        )
        return dict(self._repeatability_results)

    def get_repeatability(self):
        return dict(self._repeatability_results)

    def _validate_pipeline_tests(self, tests):
        if not isinstance(tests, (list, tuple)):
            self.logger.error(
                "Pipeline tests must be a list or tuple"
            )
            raise ValueError(
                "Pipeline tests must be a list or tuple"
            )
        for test in tests:
            if not isinstance(test, dict):
                self.logger.error(
                    "Each pipeline test must be a dictionary"
                )
                raise ValueError(
                    "Each pipeline test must be a dictionary"
                )
            if "name" not in test:
                self.logger.error(
                    "Pipeline test is missing name"
                )
                raise ValueError(
                    "Pipeline test is missing name"
                )
            if "function" not in test:
                self.logger.error(
                    "Pipeline test is missing function"
                )
                raise ValueError(
                    "Pipeline test is missing function"
                )
            if not isinstance(test["name"], str):
                self.logger.error(
                    "Pipeline test name must be a string"
                )
                raise ValueError(
                    "Pipeline test name must be a string"
                )
            if not callable(test["function"]):
                self.logger.error(
                    "Pipeline test function must be callable"
                )
                raise ValueError(
                    "Pipeline test function must be callable"
                )

    def execute_complete_pipeline(
        self,
        tests=None,
        repetitions=2
    ):
        if tests is None:
            tests = self._registered_tests
        self._validate_pipeline_tests(tests)
        if not isinstance(repetitions, int):
            self.logger.error(
                "Pipeline repetitions must be an integer"
            )
            raise ValueError(
                "Pipeline repetitions must be an integer"
            )
        if repetitions < 2:
            self.logger.error(
                "Pipeline repetitions must be at least two"
            )
            raise ValueError(
                "Pipeline repetitions must be at least two"
            )

        selected_tests = list(tests)

        self.reset()
        self.clear_test_state()

        execution_results = self.execute(
            selected_tests
        )
        execution_report = self.get_report()

        self.reset()
        coverage_report = self.analyze_coverage(
            selected_tests
        )

        self.reset()
        repeatability_report = self.analyze_repeatability(
            selected_tests,
            repetitions
        )

        self.reset()

        pipeline_success = (
            execution_report["failure"] == 0
            and execution_report["skipped"] == 0
            and len(execution_results) == len(selected_tests)
            and coverage_report["files"] >= 1
            and repeatability_report["deterministic"] is True
            and repeatability_report["state_leakage_detected"] is False
        )

        self._pipeline_results = {
            "complete": pipeline_success,
            "discovery": {
                "tests": len(selected_tests),
                "test_names": [
                    test["name"]
                    for test in selected_tests
                ]
            },
            "execution": execution_report,
            "coverage": coverage_report,
            "repeatability": repeatability_report
        }

        self.logger.info(
            f"Complete automated testing pipeline finished: "
            f"complete={pipeline_success}"
        )
        return dict(self._pipeline_results)

    def get_pipeline_results(self):
        return dict(self._pipeline_results)

    def reset(self):
        self.tests = 0
        self.success = 0
        self.failure = 0
        self.skipped = 0
        self.results = []
        self._test_state = {}
        self._coverage_results = {}
        self._repeatability_results = {}
        self._regression_results = {}
        self._pipeline_results = {}
        self.logger.info("Test runner state reset")