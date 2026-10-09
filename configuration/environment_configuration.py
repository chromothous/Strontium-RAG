import os
from collections.abc import Mapping
from classes.logger import Logger


class EnvironmentConfiguration:
    def __init__(self, logger, required_variables=(), environment_values=None):
        if not isinstance(logger, Logger):
            raise ValueError("Environment configuration logger must be a Logger")
        self.logger = logger
        if not isinstance(required_variables, (list, tuple)):
            self.logger.error("Required environment variables must be a list or tuple.")
            raise ValueError("Required environment variables must be a list or tuple")
        normalized_variables = []
        for variable in required_variables:
            if not isinstance(variable, str) or not variable.strip():
                self.logger.error("Environment variable names must be non-empty strings.")
                raise ValueError("Environment variable names must be non-empty strings")
            normalized_variables.append(variable.strip())
        if environment_values is not None and not isinstance(environment_values, Mapping):
            self.logger.error("Environment values must be a mapping.")
            raise ValueError("Environment values must be a mapping")
        self.required_variables = tuple(dict.fromkeys(normalized_variables))
        self._environment_values = os.environ if environment_values is None else environment_values
        self.logger.info(f"Environment configuration initialized with {len(self.required_variables)} required variables.")

    def _validate_name(self, name):
        if not isinstance(name, str) or not name.strip():
            self.logger.error("Environment variable name must be a non-empty string.")
            raise ValueError("Environment variable name must be a non-empty string")
        return name.strip()

    def get(self, name, default=None):
        name = self._validate_name(name)
        value = self._environment_values.get(name, default)
        if value is not None and not isinstance(value, str):
            self.logger.error(f"Environment variable {name} must contain a string value.")
            raise ValueError(f"Environment variable {name} must contain a string value")
        return value

    def is_present(self, name):
        value = self.get(name)
        return isinstance(value, str) and bool(value.strip())

    def require(self, name):
        name = self._validate_name(name)
        value = self.get(name)
        if not isinstance(value, str) or not value.strip():
            message = f"Required environment variable is missing or empty: {name}"
            self.logger.error(message)
            raise RuntimeError(message)
        return value

    def validate_required(self):
        missing_variables = [
            name for name in self.required_variables
            if not self.is_present(name)
        ]
        if missing_variables:
            message = "Required environment variables are missing or empty: " + ", ".join(missing_variables)
            self.logger.error(message)
            raise RuntimeError(message)
        self.logger.info(f"Environment configuration validation passed: {len(self.required_variables)} required variables checked.")
        return True

    def get_definition(self):
        present_variables = tuple(
            name for name in self.required_variables
            if self.is_present(name)
        )
        missing_variables = tuple(
            name for name in self.required_variables
            if name not in present_variables
        )
        return {
            "required_variables": self.required_variables,
            "present_required_variables": present_variables,
            "missing_required_variables": missing_variables,
        }