class StrontiumError(Exception):
    STANDARD_CATEGORIES = (
        "validation",
        "retrieval",
        "context",
        "generation",
        "citation",
        "evaluation",
        "system"
    )
    SPECIAL_CATEGORIES = (
        "unexpected",
    )
    VALID_CATEGORIES = STANDARD_CATEGORIES + SPECIAL_CATEGORIES

    def __init__(
        self,
        message,
        category="system",
        component=None,
        operation=None,
        details=None,
        cause=None,
        expected=True,
        propagation=None
    ):
        self.message = message
        self.category = category
        self.component = component
        self.operation = operation
        self.details = details if details is not None else {}
        self.cause = cause
        self.expected = expected
        self.propagation = (
            list(propagation)
            if propagation is not None
            else []
        )
        self.validate()
        super().__init__(self.message)

    @classmethod
    def get_standard_categories(cls):
        return tuple(cls.STANDARD_CATEGORIES)

    @classmethod
    def get_valid_categories(cls):
        return tuple(cls.VALID_CATEGORIES)

    @classmethod
    def is_valid_category(cls, category):
        return (
            isinstance(category, str)
            and category in cls.VALID_CATEGORIES
        )

    @classmethod
    def is_standard_category(cls, category):
        return (
            isinstance(category, str)
            and category in cls.STANDARD_CATEGORIES
        )

    def validate(self):
        if not isinstance(self.message, str):
            raise ValueError("Error message must be a string")
        if not self.message.strip():
            raise ValueError("Error message cannot be empty")
        if not isinstance(self.category, str):
            raise ValueError("Error category must be a string")
        if not self.category.strip():
            raise ValueError("Error category cannot be empty")
        if not self.is_valid_category(self.category):
            raise ValueError(
                f"Invalid error category: {self.category}"
            )
        if self.component is not None:
            if not isinstance(self.component, str):
                raise ValueError(
                    "Error component must be a string or None"
                )
            if not self.component.strip():
                raise ValueError(
                    "Error component cannot be empty"
                )
        if self.operation is not None:
            if not isinstance(self.operation, str):
                raise ValueError(
                    "Error operation must be a string or None"
                )
            if not self.operation.strip():
                raise ValueError(
                    "Error operation cannot be empty"
                )
        if not isinstance(self.details, dict):
            raise ValueError(
                "Error details must be a dictionary"
            )
        if self.cause is not None:
            if not isinstance(self.cause, Exception):
                raise ValueError(
                    "Error cause must be an exception or None"
                )
        if not isinstance(self.expected, bool):
            raise ValueError(
                "Error expected flag must be a boolean"
            )
        if not isinstance(self.propagation, list):
            raise ValueError(
                "Error propagation must be a list"
            )
        for propagation_step in self.propagation:
            if not isinstance(propagation_step, dict):
                raise ValueError(
                    "Each propagation step must be a dictionary"
                )
            if "component" not in propagation_step:
                raise ValueError(
                    "Propagation step is missing component"
                )
            if "operation" not in propagation_step:
                raise ValueError(
                    "Propagation step is missing operation"
                )
            if not isinstance(
                propagation_step["component"],
                str
            ):
                raise ValueError(
                    "Propagation component must be a string"
                )
            if not propagation_step["component"].strip():
                raise ValueError(
                    "Propagation component cannot be empty"
                )
            if not isinstance(
                propagation_step["operation"],
                str
            ):
                raise ValueError(
                    "Propagation operation must be a string"
                )
            if not propagation_step["operation"].strip():
                raise ValueError(
                    "Propagation operation cannot be empty"
                )
        if self.category == "unexpected":
            if self.expected is True:
                raise ValueError(
                    "Unexpected errors must be marked as unexpected"
                )
            if self.cause is None:
                raise ValueError(
                    "Unexpected errors must preserve their original exception"
                )
        return True

    def is_valid(self):
        try:
            self.validate()
            return True
        except ValueError:
            return False

    def is_expected(self):
        return self.expected

    def is_unexpected(self):
        return not self.expected

    def add_propagation(self, component, operation):
        if not isinstance(component, str):
            raise ValueError(
                "Propagation component must be a string"
            )
        if not component.strip():
            raise ValueError(
                "Propagation component cannot be empty"
            )
        if not isinstance(operation, str):
            raise ValueError(
                "Propagation operation must be a string"
            )
        if not operation.strip():
            raise ValueError(
                "Propagation operation cannot be empty"
            )
        propagation_step = {
            "component": component,
            "operation": operation
        }
        self.propagation.append(
            propagation_step
        )
        self.validate()
        return propagation_step

    def get_propagation(self):
        return [
            dict(step)
            for step in self.propagation
        ]

    def get_error_path(self):
        path = []
        if self.component is not None:
            path.append(
                {
                    "component": self.component,
                    "operation": self.operation
                }
            )
        path.extend(
            self.get_propagation()
        )
        return path

    def to_dict(self):
        return {
            "message": self.message,
            "category": self.category,
            "component": self.component,
            "operation": self.operation,
            "details": dict(self.details),
            "cause": str(self.cause) if self.cause is not None else None,
            "expected": self.expected,
            "propagation": self.get_propagation()
        }

    def __str__(self):
        return self.message


class ErrorHandler:
    def __init__(self):
        self.errors = []
        self._isolated_states = {}

    def validate_category(self, category):
        if not isinstance(category, str):
            raise ValueError("Error category must be a string")
        if not category.strip():
            raise ValueError("Error category cannot be empty")
        if not StrontiumError.is_valid_category(category):
            raise ValueError(
                f"Invalid error category: {category}"
            )
        return category

    def validate_error(self, error):
        if not isinstance(error, StrontiumError):
            raise ValueError(
                "Error must be a StrontiumError"
            )
        error.validate()
        return True

    def validate_definition(self, definition):
        if not isinstance(definition, dict):
            raise ValueError(
                "Error definition must be a dictionary"
            )
        required_fields = {
            "message",
            "category",
            "expected"
        }
        missing_fields = required_fields - set(
            definition.keys()
        )
        if missing_fields:
            raise ValueError(
                f"Error definition is missing required fields: {missing_fields}"
            )
        return True

    def create_from_definition(self, definition):
        self.validate_definition(definition)
        return self.create_error(
            message=definition["message"],
            category=definition["category"],
            component=definition.get("component"),
            operation=definition.get("operation"),
            details=definition.get("details"),
            cause=definition.get("cause"),
            expected=definition["expected"],
            propagation=definition.get("propagation")
        )

    def create_error(
        self,
        message,
        category="system",
        component=None,
        operation=None,
        details=None,
        cause=None,
        expected=True,
        propagation=None
    ):
        self.validate_category(category)
        error = StrontiumError(
            message=message,
            category=category,
            component=component,
            operation=operation,
            details=details,
            cause=cause,
            expected=expected,
            propagation=propagation
        )
        self.validate_error(error)
        self.errors.append(error)
        return error

    def handle_expected(
        self,
        message,
        category="system",
        component=None,
        operation=None,
        details=None,
        cause=None
    ):
        return self.create_error(
            message=message,
            category=category,
            component=component,
            operation=operation,
            details=details,
            cause=cause,
            expected=True
        )

    def handle_unexpected(
        self,
        exception,
        component=None,
        operation=None,
        details=None
    ):
        if not isinstance(exception, Exception):
            raise ValueError(
                "Unexpected error must be an exception"
            )
        return self.create_error(
            message=str(exception),
            category="unexpected",
            component=component,
            operation=operation,
            details=details,
            cause=exception,
            expected=False
        )

    def propagate(
        self,
        error,
        component,
        operation
    ):
        self.validate_error(error)
        error.add_propagation(
            component,
            operation
        )
        if not any(
            stored_error is error
            for stored_error in self.errors
        ):
            self.errors.append(error)
        self.validate_error(error)
        return error

    def begin_isolation(self, name, state):
        if not isinstance(name, str):
            raise ValueError(
                "Isolation name must be a string"
            )
        if not name.strip():
            raise ValueError(
                "Isolation name cannot be empty"
            )
        if not isinstance(state, dict):
            raise ValueError(
                "Isolated state must be a dictionary"
            )
        if name in self._isolated_states:
            raise ValueError(
                f"Isolation boundary already exists: {name}"
            )
        self._isolated_states[name] = {
            "original": dict(state),
            "working": dict(state)
        }
        return dict(
            self._isolated_states[name]["working"]
        )

    def get_isolated_state(self, name):
        if name not in self._isolated_states:
            raise ValueError(
                f"Isolation boundary not found: {name}"
            )
        return dict(
            self._isolated_states[name]["working"]
        )

    def update_isolated_state(self, name, key, value):
        if name not in self._isolated_states:
            raise ValueError(
                f"Isolation boundary not found: {name}"
            )
        if not isinstance(key, str):
            raise ValueError(
                "Isolated state key must be a string"
            )
        if not key.strip():
            raise ValueError(
                "Isolated state key cannot be empty"
            )
        self._isolated_states[name]["working"][key] = value
        return self.get_isolated_state(name)

    def commit_isolation(self, name, target_state):
        if name not in self._isolated_states:
            raise ValueError(
                f"Isolation boundary not found: {name}"
            )
        if not isinstance(target_state, dict):
            raise ValueError(
                "Isolation target state must be a dictionary"
            )
        working_state = self._isolated_states[name]["working"]
        target_state.clear()
        target_state.update(working_state)
        committed_state = dict(target_state)
        del self._isolated_states[name]
        return committed_state

    def rollback_isolation(self, name, target_state):
        if name not in self._isolated_states:
            raise ValueError(
                f"Isolation boundary not found: {name}"
            )
        if not isinstance(target_state, dict):
            raise ValueError(
                "Isolation target state must be a dictionary"
            )
        original_state = self._isolated_states[name]["original"]
        target_state.clear()
        target_state.update(original_state)
        restored_state = dict(target_state)
        del self._isolated_states[name]
        return restored_state

    def isolate_operation(
        self,
        name,
        state,
        operation
    ):
        if not callable(operation):
            raise ValueError(
                "Isolated operation must be callable"
            )
        self.begin_isolation(
            name,
            state
        )
        try:
            working_state = self._isolated_states[name]["working"]
            result = operation(
                working_state
            )
            committed_state = self.commit_isolation(
                name,
                state
            )
            return {
                "success": True,
                "result": result,
                "state": committed_state,
                "error": None
            }
        except StrontiumError as error:
            self.rollback_isolation(
                name,
                state
            )
            self.propagate(
                error,
                error.component or "unknown",
                error.operation or name
            )
            return {
                "success": False,
                "result": None,
                "state": dict(state),
                "error": error
            }
        except Exception as exception:
            self.rollback_isolation(
                name,
                state
            )
            error = self.handle_unexpected(
                exception,
                component=name
            )
            return {
                "success": False,
                "result": None,
                "state": dict(state),
                "error": error
            }

    def get_isolation_boundaries(self):
        return {
            name: {
                "original": dict(data["original"]),
                "working": dict(data["working"])
            }
            for name, data in self._isolated_states.items()
        }

    def classify(self, category):
        return self.validate_category(category)

    def get_errors(self):
        return list(self.errors)

    def get_expected_errors(self):
        return [
            error
            for error in self.errors
            if error.is_expected()
        ]

    def get_unexpected_errors(self):
        return [
            error
            for error in self.errors
            if error.is_unexpected()
        ]

    def get_errors_by_category(self, category):
        self.validate_category(category)
        return [
            error
            for error in self.errors
            if error.category == category
        ]

    def clear(self):
        self.errors = []
        self._isolated_states = {}