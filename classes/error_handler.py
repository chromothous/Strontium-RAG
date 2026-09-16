class StrontiumError:
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
        expected=True
    ):
        self.message = message
        self.category = category
        self.component = component
        self.operation = operation
        self.details = details if details is not None else {}
        self.cause = cause
        self.expected = expected
        self.validate()

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

    def to_dict(self):
        return {
            "message": self.message,
            "category": self.category,
            "component": self.component,
            "operation": self.operation,
            "details": dict(self.details),
            "cause": str(self.cause) if self.cause is not None else None,
            "expected": self.expected
        }

    def __str__(self):
        return self.message


class ErrorHandler:
    def __init__(self):
        self.errors = []

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
        missing_fields = required_fields - set(definition.keys())
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
            expected=definition["expected"]
        )

    def create_error(
        self,
        message,
        category="system",
        component=None,
        operation=None,
        details=None,
        cause=None,
        expected=True
    ):
        self.validate_category(category)
        error = StrontiumError(
            message=message,
            category=category,
            component=component,
            operation=operation,
            details=details,
            cause=cause,
            expected=expected
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