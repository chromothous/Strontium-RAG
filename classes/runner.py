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