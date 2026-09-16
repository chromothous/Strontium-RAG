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
        propagation=None,
        recoverable=False
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
        self.recoverable = recoverable
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
        if not isinstance(self.recoverable, bool):
            raise ValueError(
                "Error recoverable flag must be a boolean"
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
            if self.recoverable is True:
                raise ValueError(
                    "Unexpected errors cannot be marked as recoverable"
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

    def is_recoverable(self):
        return self.recoverable

    def is_non_recoverable(self):
        return not self.recoverable

    def mark_recoverable(self):
        if self.category == "unexpected":
            raise ValueError(
                "Unexpected errors cannot be marked as recoverable"
            )
        self.recoverable = True
        self.validate()
        return self.recoverable

    def mark_non_recoverable(self):
        self.recoverable = False
        self.validate()
        return self.recoverable

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
            "propagation": self.get_propagation(),
            "recoverable": self.recoverable
        }

    def __str__(self):
        return self.message


class ErrorHandler:
    def __init__(self):
        self.errors = []
        self._isolated_states = {}
        self._recovery_history = []
        self._retry_history = []
        self._fallback_history = []

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
            propagation=definition.get("propagation"),
            recoverable=definition.get(
                "recoverable",
                False
            )
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
        propagation=None,
        recoverable=False
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
            propagation=propagation,
            recoverable=recoverable
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
        cause=None,
        recoverable=False
    ):
        return self.create_error(
            message=message,
            category=category,
            component=component,
            operation=operation,
            details=details,
            cause=cause,
            expected=True,
            recoverable=recoverable
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
            expected=False,
            recoverable=False
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

    def recover(
        self,
        error,
        recovery_operation
    ):
        self.validate_error(error)
        if not error.is_recoverable():
            raise ValueError(
                "Non-recoverable errors cannot be recovered"
            )
        if not callable(recovery_operation):
            raise ValueError(
                "Recovery operation must be callable"
            )
        recovery_record = {
            "error": error,
            "success": False,
            "result": None
        }
        try:
            result = recovery_operation()
            recovery_record["success"] = True
            recovery_record["result"] = result
            self._recovery_history.append(
                recovery_record
            )
            return {
                "success": True,
                "result": result,
                "error": error
            }
        except StrontiumError as recovery_error:
            self._recovery_history.append(
                recovery_record
            )
            self.propagate(
                recovery_error,
                recovery_error.component or "recovery",
                recovery_error.operation or "recover"
            )
            return {
                "success": False,
                "result": None,
                "error": recovery_error
            }
        except Exception as exception:
            recovery_error = self.handle_unexpected(
                exception,
                component="recovery",
                operation="recover"
            )
            self._recovery_history.append(
                recovery_record
            )
            return {
                "success": False,
                "result": None,
                "error": recovery_error
            }

    def recover_isolated_operation(
        self,
        name,
        state,
        error,
        recovery_operation
    ):
        self.validate_error(error)
        if not error.is_recoverable():
            raise ValueError(
                "Non-recoverable errors cannot be recovered"
            )
        if not callable(recovery_operation):
            raise ValueError(
                "Recovery operation must be callable"
            )
        self.begin_isolation(
            name,
            state
        )
        try:
            working_state = self._isolated_states[name]["working"]
            result = recovery_operation(
                working_state
            )
            recovered_state = self.commit_isolation(
                name,
                state
            )
            recovery_record = {
                "error": error,
                "success": True,
                "result": result
            }
            self._recovery_history.append(
                recovery_record
            )
            return {
                "success": True,
                "result": result,
                "state": recovered_state,
                "error": error
            }
        except StrontiumError as recovery_error:
            self.rollback_isolation(
                name,
                state
            )
            self._recovery_history.append(
                {
                    "error": error,
                    "success": False,
                    "result": None
                }
            )
            self.propagate(
                recovery_error,
                recovery_error.component or "recovery",
                recovery_error.operation or "recover"
            )
            return {
                "success": False,
                "result": None,
                "state": dict(state),
                "error": recovery_error
            }
        except Exception as exception:
            self.rollback_isolation(
                name,
                state
            )
            recovery_error = self.handle_unexpected(
                exception,
                component="recovery",
                operation="recover"
            )
            self._recovery_history.append(
                {
                    "error": error,
                    "success": False,
                    "result": None
                }
            )
            return {
                "success": False,
                "result": None,
                "state": dict(state),
                "error": recovery_error
            }

    def get_recovery_history(self):
        return list(self._recovery_history)

    def get_successful_recoveries(self):
        return [
            recovery
            for recovery in self._recovery_history
            if recovery["success"]
        ]

    def get_failed_recoveries(self):
        return [
            recovery
            for recovery in self._recovery_history
            if not recovery["success"]
        ]

    def retry(
        self,
        operation,
        max_attempts,
        error_handler=None
    ):
        if not callable(operation):
            raise ValueError(
                "Retry operation must be callable"
            )
        if not isinstance(max_attempts, int):
            raise ValueError(
                "Maximum retry attempts must be an integer"
            )
        if max_attempts < 1:
            raise ValueError(
                "Maximum retry attempts must be at least 1"
            )
        if error_handler is not None:
            if not callable(error_handler):
                raise ValueError(
                    "Retry error handler must be callable"
                )
        retry_record = {
            "attempts": [],
            "success": False,
            "result": None,
            "error": None
        }
        for attempt in range(1, max_attempts + 1):
            attempt_record = {
                "attempt": attempt,
                "success": False,
                "result": None,
                "error": None
            }
            try:
                result = operation()
                attempt_record["success"] = True
                attempt_record["result"] = result
                retry_record["attempts"].append(
                    attempt_record
                )
                retry_record["success"] = True
                retry_record["result"] = result
                self._retry_history.append(
                    retry_record
                )
                return {
                    "success": True,
                    "attempts": attempt,
                    "result": result,
                    "error": None
                }
            except StrontiumError as error:
                self.validate_error(error)
                attempt_record["error"] = error
                retry_record["attempts"].append(
                    attempt_record
                )
                retry_record["error"] = error
                if not error.is_recoverable():
                    break
                if error_handler is not None:
                    error_handler(
                        error,
                        attempt
                    )
            except Exception as exception:
                error = self.handle_unexpected(
                    exception,
                    component="retry",
                    operation="attempt"
                )
                attempt_record["error"] = error
                retry_record["attempts"].append(
                    attempt_record
                )
                retry_record["error"] = error
                break
        self._retry_history.append(
            retry_record
        )
        final_error = retry_record["error"]
        return {
            "success": False,
            "attempts": len(
                retry_record["attempts"]
            ),
            "result": None,
            "error": final_error
        }

    def retry_recoverable(
        self,
        error,
        operation,
        max_attempts
    ):
        self.validate_error(error)
        if not error.is_recoverable():
            raise ValueError(
                "Only recoverable errors can be retried"
            )
        if not callable(operation):
            raise ValueError(
                "Retry operation must be callable"
            )
        if not isinstance(max_attempts, int):
            raise ValueError(
                "Maximum retry attempts must be an integer"
            )
        if max_attempts < 1:
            raise ValueError(
                "Maximum retry attempts must be at least 1"
            )
        retry_record = {
            "attempts": [],
            "success": False,
            "result": None,
            "error": error
        }
        for attempt in range(1, max_attempts + 1):
            attempt_record = {
                "attempt": attempt,
                "success": False,
                "result": None,
                "error": None
            }
            try:
                result = operation()
                attempt_record["success"] = True
                attempt_record["result"] = result
                retry_record["attempts"].append(
                    attempt_record
                )
                retry_record["success"] = True
                retry_record["result"] = result
                retry_record["error"] = None
                self._retry_history.append(
                    retry_record
                )
                return {
                    "success": True,
                    "attempts": attempt,
                    "result": result,
                    "error": None
                }
            except StrontiumError as retry_error:
                self.validate_error(retry_error)
                attempt_record["error"] = retry_error
                retry_record["attempts"].append(
                    attempt_record
                )
                retry_record["error"] = retry_error
                if not retry_error.is_recoverable():
                    break
            except Exception as exception:
                retry_error = self.handle_unexpected(
                    exception,
                    component=error.component or "retry",
                    operation=error.operation or "attempt"
                )
                attempt_record["error"] = retry_error
                retry_record["attempts"].append(
                    attempt_record
                )
                retry_record["error"] = retry_error
                break
        self._retry_history.append(
            retry_record
        )
        return {
            "success": False,
            "attempts": len(
                retry_record["attempts"]
            ),
            "result": None,
            "error": retry_record["error"]
        }

    def get_retry_history(self):
        return list(self._retry_history)

    def get_successful_retries(self):
        return [
            retry
            for retry in self._retry_history
            if retry["success"]
        ]

    def get_failed_retries(self):
        return [
            retry
            for retry in self._retry_history
            if not retry["success"]
        ]

    def fallback(
        self,
        primary_operation,
        fallback_operation
    ):
        if not callable(primary_operation):
            raise ValueError(
                "Primary operation must be callable"
            )
        if not callable(fallback_operation):
            raise ValueError(
                "Fallback operation must be callable"
            )
        fallback_record = {
            "primary_success": False,
            "fallback_used": False,
            "success": False,
            "primary_error": None,
            "fallback_error": None,
            "result": None
        }
        try:
            result = primary_operation()
            fallback_record["primary_success"] = True
            fallback_record["success"] = True
            fallback_record["result"] = result
            self._fallback_history.append(
                fallback_record
            )
            return {
                "success": True,
                "fallback_used": False,
                "result": result,
                "error": None
            }
        except StrontiumError as primary_error:
            self.validate_error(primary_error)
            fallback_record["primary_error"] = primary_error
            if not primary_error.is_recoverable():
                self._fallback_history.append(
                    fallback_record
                )
                return {
                    "success": False,
                    "fallback_used": False,
                    "result": None,
                    "error": primary_error
                }
        except Exception as exception:
            primary_error = self.handle_unexpected(
                exception,
                component="fallback",
                operation="primary"
            )
            fallback_record["primary_error"] = primary_error
            self._fallback_history.append(
                fallback_record
            )
            return {
                "success": False,
                "fallback_used": False,
                "result": None,
                "error": primary_error
            }
        fallback_record["fallback_used"] = True
        try:
            result = fallback_operation()
            fallback_record["success"] = True
            fallback_record["result"] = result
            self._fallback_history.append(
                fallback_record
            )
            return {
                "success": True,
                "fallback_used": True,
                "result": result,
                "error": fallback_record["primary_error"]
            }
        except StrontiumError as fallback_error:
            self.validate_error(fallback_error)
            fallback_record["fallback_error"] = fallback_error
            self._fallback_history.append(
                fallback_record
            )
            self.propagate(
                fallback_error,
                fallback_error.component or "fallback",
                fallback_error.operation or "alternate"
            )
            return {
                "success": False,
                "fallback_used": True,
                "result": None,
                "error": fallback_error
            }
        except Exception as exception:
            fallback_error = self.handle_unexpected(
                exception,
                component="fallback",
                operation="alternate"
            )
            fallback_record["fallback_error"] = fallback_error
            self._fallback_history.append(
                fallback_record
            )
            return {
                "success": False,
                "fallback_used": True,
                "result": None,
                "error": fallback_error
            }

    def get_fallback_history(self):
        return list(self._fallback_history)

    def get_successful_fallbacks(self):
        return [
            fallback
            for fallback in self._fallback_history
            if fallback["success"]
            and fallback["fallback_used"]
        ]

    def get_failed_fallbacks(self):
        return [
            fallback
            for fallback in self._fallback_history
            if not fallback["success"]
        ]

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
        self._recovery_history = []
        self._retry_history = []
        self._fallback_history = []