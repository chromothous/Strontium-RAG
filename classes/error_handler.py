class StrontiumError:
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
        if not isinstance(message, str):
            raise ValueError("Error message must be a string")
        if not message.strip():
            raise ValueError("Error message cannot be empty")
        if not isinstance(category, str):
            raise ValueError("Error category must be a string")
        if not category.strip():
            raise ValueError("Error category cannot be empty")
        if component is not None and not isinstance(component, str):
            raise ValueError("Error component must be a string or None")
        if operation is not None and not isinstance(operation, str):
            raise ValueError("Error operation must be a string or None")
        if details is not None and not isinstance(details, dict):
            raise ValueError("Error details must be a dictionary or None")
        if cause is not None and not isinstance(cause, Exception):
            raise ValueError("Error cause must be an exception or None")
        if not isinstance(expected, bool):
            raise ValueError("Error expected flag must be a boolean")

        self.message = message
        self.category = category
        self.component = component
        self.operation = operation
        self.details = dict(details) if details is not None else {}
        self.cause = cause
        self.expected = expected

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
        error = StrontiumError(
            message=message,
            category=category,
            component=component,
            operation=operation,
            details=details,
            cause=cause,
            expected=expected
        )
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

    def clear(self):
        self.errors = []