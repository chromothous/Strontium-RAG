import os
from collections.abc import Mapping
from classes.logger import Logger


class EnvironmentConfiguration:
    def __init__(
        self,
        logger,
        required_variables=(),
        environment_values=None,
        required_secrets=(),
        required_provider_variables=(),
    ):
        if not isinstance(logger, Logger):
            raise ValueError("Environment configuration logger must be a Logger")
        self.logger = logger
        self.required_variables = self._normalize_names(
            required_variables,
            "Required environment variables must be a list or tuple",
            "Environment variable names must be non-empty strings",
        )
        self.required_secrets = self._normalize_names(
            required_secrets,
            "Required secrets must be a list or tuple",
            "Secret environment variable names must be non-empty strings",
        )
        self.required_provider_variables = self._normalize_names(
            required_provider_variables,
            "Required provider variables must be a list or tuple",
            "Provider configuration variable names must be non-empty strings",
        )
        if environment_values is not None and not isinstance(environment_values, Mapping):
            self.logger.error("Environment values must be a mapping.")
            raise ValueError("Environment values must be a mapping")
        self._environment_values = os.environ if environment_values is None else environment_values
        self.logger.info(
            "Environment configuration initialized: "
            f"{len(self.required_variables)} general variables, "
            f"{len(self.required_secrets)} secrets, "
            f"{len(self.required_provider_variables)} provider variables."
        )

    def _normalize_names(self, names, collection_error, name_error):
        if not isinstance(names, (list, tuple)):
            self.logger.error(collection_error + ".")
            raise ValueError(collection_error)
        normalized_names = []
        for name in names:
            if not isinstance(name, str) or not name.strip():
                self.logger.error(name_error + ".")
                raise ValueError(name_error)
            normalized_names.append(name.strip())
        return tuple(dict.fromkeys(normalized_names))

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

    def require_secret(self, name):
        name = self._validate_name(name)
        if name not in self.required_secrets:
            message = f"Environment variable is not registered as a required secret: {name}"
            self.logger.error(message)
            raise ValueError(message)
        value = self.get(name)
        if not isinstance(value, str) or not value.strip():
            message = f"Required secret environment variable is missing or empty: {name}"
            self.logger.error(message)
            raise RuntimeError(message)
        return value

    def validate_secrets(self):
        missing_secrets = tuple(
            name for name in self.required_secrets
            if not self.is_present(name)
        )
        if missing_secrets:
            message = (
                "Required secret environment variables are missing or empty: "
                + ", ".join(missing_secrets)
            )
            self.logger.error(message)
            raise RuntimeError(message)
        self.logger.info(
            f"Secret validation passed: {len(self.required_secrets)} secrets checked."
        )
        return True

    def validate_provider_configuration(self):
        missing_variables = tuple(
            name for name in self.required_provider_variables
            if not self.is_present(name)
        )
        if missing_variables:
            message = (
                "Required provider configuration variables are missing or empty: "
                + ", ".join(missing_variables)
            )
            self.logger.error(message)
            raise RuntimeError(message)
        self.logger.info(
            "Provider configuration validation passed: "
            f"{len(self.required_provider_variables)} variables checked."
        )
        return True

    def validate_required(self):
        missing_variables = tuple(
            name for name in self.required_variables
            if not self.is_present(name)
        )
        missing_secrets = tuple(
            name for name in self.required_secrets
            if not self.is_present(name)
        )
        missing_provider_variables = tuple(
            name for name in self.required_provider_variables
            if not self.is_present(name)
        )
        failures = []
        if missing_variables:
            failures.append(
                "required environment variables are missing or empty: "
                + ", ".join(missing_variables)
            )
        if missing_secrets:
            failures.append(
                "required secret environment variables are missing or empty: "
                + ", ".join(missing_secrets)
            )
        if missing_provider_variables:
            failures.append(
                "required provider configuration variables are missing or empty: "
                + ", ".join(missing_provider_variables)
            )
        if failures:
            message = "Required configuration is invalid: " + "; ".join(failures)
            self.logger.error(message)
            raise RuntimeError(message)
        total = (
            len(self.required_variables)
            + len(self.required_secrets)
            + len(self.required_provider_variables)
        )
        self.logger.info(
            f"Environment configuration validation passed: {total} requirements checked."
        )
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
        present_secrets = tuple(
            name for name in self.required_secrets
            if self.is_present(name)
        )
        missing_secrets = tuple(
            name for name in self.required_secrets
            if name not in present_secrets
        )
        present_provider_variables = tuple(
            name for name in self.required_provider_variables
            if self.is_present(name)
        )
        missing_provider_variables = tuple(
            name for name in self.required_provider_variables
            if name not in present_provider_variables
        )
        return {
            "required_variables": self.required_variables,
            "present_required_variables": present_variables,
            "missing_required_variables": missing_variables,
            "required_secrets": self.required_secrets,
            "present_required_secrets": present_secrets,
            "missing_required_secrets": missing_secrets,
            "required_provider_variables": self.required_provider_variables,
            "present_required_provider_variables": present_provider_variables,
            "missing_required_provider_variables": missing_provider_variables,
        }