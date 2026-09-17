from classes.logger import Logger
from classes.error_handler import ErrorHandler


class SecurityError(Exception):
    def __init__(
        self,
        message,
        category="security"
    ):
        if not isinstance(message, str) or not message.strip():
            raise ValueError(
                "Security error message must be a non-empty string"
            )
        if not isinstance(category, str) or not category.strip():
            raise ValueError(
                "Security error category must be a non-empty string"
            )
        self.message = message
        self.category = category
        super().__init__(message)

    def __str__(self):
        return self.message


class SecurityValidationError(SecurityError):
    def __init__(
        self,
        message,
        field=None
    ):
        super().__init__(
            message,
            category="validation"
        )
        if field is not None:
            if not isinstance(field, str) or not field.strip():
                raise ValueError(
                    "Security validation field must be a non-empty string or None"
                )
        self.field = field


class SecurityPolicyError(SecurityError):
    def __init__(
        self,
        message,
        policy=None
    ):
        super().__init__(
            message,
            category="policy"
        )
        if policy is not None and not isinstance(policy, SecurityPolicy):
            raise ValueError(
                "Security policy must be a SecurityPolicy or None"
            )
        self.policy = policy


class ValidationResult:
    def __init__(
        self,
        valid,
        value=None,
        errors=None,
        warnings=None,
        trusted=False,
        boundary=None
    ):
        if not isinstance(valid, bool):
            raise ValueError(
                "Validation result valid flag must be a boolean"
            )
        if errors is None:
            errors = []
        if warnings is None:
            warnings = []
        if not isinstance(errors, list):
            raise ValueError(
                "Validation result errors must be a list"
            )
        if not isinstance(warnings, list):
            raise ValueError(
                "Validation result warnings must be a list"
            )
        if not isinstance(trusted, bool):
            raise ValueError(
                "Validation result trusted flag must be a boolean"
            )
        if boundary is not None:
            if not isinstance(boundary, str) or not boundary.strip():
                raise ValueError(
                    "Validation result boundary must be a non-empty string or None"
                )
        if trusted and not valid:
            raise ValueError(
                "Invalid validation results cannot be trusted"
            )

        self.valid = valid
        self.value = value
        self.errors = list(errors)
        self.warnings = list(warnings)
        self.trusted = trusted
        self.boundary = boundary

    def is_valid(self):
        return self.valid is True

    def is_invalid(self):
        return self.valid is False

    def is_trusted(self):
        return self.trusted is True

    def is_untrusted(self):
        return self.trusted is False

    def to_dict(self):
        return {
            "valid": self.valid,
            "value": self.value,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "trusted": self.trusted,
            "boundary": self.boundary
        }


class SecurityPolicy:
    DEFAULT_MAX_STRING_LENGTH = 10000
    DEFAULT_MAX_COLLECTION_SIZE = 1000
    DEFAULT_MAX_METADATA_SIZE = 100
    DEFAULT_MAX_NESTING_DEPTH = 10
    DEFAULT_ALLOWED_SCHEMES = (
        "https",
    )
    DEFAULT_ALLOWED_FILE_TYPES = (
        ".txt",
    )

    def __init__(
        self,
        max_string_length=DEFAULT_MAX_STRING_LENGTH,
        max_collection_size=DEFAULT_MAX_COLLECTION_SIZE,
        max_metadata_size=DEFAULT_MAX_METADATA_SIZE,
        max_nesting_depth=DEFAULT_MAX_NESTING_DEPTH,
        allowed_schemes=None,
        allowed_file_types=None
    ):
        self.max_string_length = self._validate_positive_integer(
            max_string_length,
            "max string length"
        )
        self.max_collection_size = self._validate_positive_integer(
            max_collection_size,
            "max collection size"
        )
        self.max_metadata_size = self._validate_positive_integer(
            max_metadata_size,
            "max metadata size"
        )
        self.max_nesting_depth = self._validate_positive_integer(
            max_nesting_depth,
            "max nesting depth"
        )

        if allowed_schemes is None:
            allowed_schemes = self.DEFAULT_ALLOWED_SCHEMES
        if allowed_file_types is None:
            allowed_file_types = self.DEFAULT_ALLOWED_FILE_TYPES

        if not isinstance(allowed_schemes, (list, tuple)):
            raise ValueError(
                "Security allowed schemes must be a list or tuple"
            )
        if not allowed_schemes:
            raise ValueError(
                "Security allowed schemes cannot be empty"
            )

        if not isinstance(allowed_file_types, (list, tuple)):
            raise ValueError(
                "Security allowed file types must be a list or tuple"
            )
        if not allowed_file_types:
            raise ValueError(
                "Security allowed file types cannot be empty"
            )

        normalized_schemes = []
        for scheme in allowed_schemes:
            if not isinstance(scheme, str) or not scheme.strip():
                raise ValueError(
                    "Security schemes must contain non-empty strings"
                )
            normalized_schemes.append(
                scheme.strip().lower()
            )

        normalized_file_types = []
        for file_type in allowed_file_types:
            if not isinstance(file_type, str) or not file_type.strip():
                raise ValueError(
                    "Security file types must contain non-empty strings"
                )
            normalized_file_types.append(
                file_type.strip().lower()
            )

        self.allowed_schemes = tuple(
            normalized_schemes
        )
        self.allowed_file_types = tuple(
            normalized_file_types
        )

    def _validate_positive_integer(
        self,
        value,
        name
    ):
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(
                f"Security {name} must be a positive integer"
            )
        if value <= 0:
            raise ValueError(
                f"Security {name} must be a positive integer"
            )
        return value

    def validate(self):
        self._validate_positive_integer(
            self.max_string_length,
            "max string length"
        )
        self._validate_positive_integer(
            self.max_collection_size,
            "max collection size"
        )
        self._validate_positive_integer(
            self.max_metadata_size,
            "max metadata size"
        )
        self._validate_positive_integer(
            self.max_nesting_depth,
            "max nesting depth"
        )

        if not self.allowed_schemes:
            raise ValueError(
                "Security allowed schemes cannot be empty"
            )

        if not self.allowed_file_types:
            raise ValueError(
                "Security allowed file types cannot be empty"
            )

        return True

    def to_dict(self):
        return {
            "max_string_length": self.max_string_length,
            "max_collection_size": self.max_collection_size,
            "max_metadata_size": self.max_metadata_size,
            "max_nesting_depth": self.max_nesting_depth,
            "allowed_schemes": tuple(
                self.allowed_schemes
            ),
            "allowed_file_types": tuple(
                self.allowed_file_types
            )
        }


class TrustBoundary:
    USER_QUERY = "user_query"
    DOCUMENT = "document"
    METADATA = "metadata"
    CONFIGURATION = "configuration"
    FILE_PATH = "file_path"
    URL = "url"
    PROVIDER_MODEL = "provider_model"
    CONVERSATION_STATE = "conversation_state"
    EXTERNAL_RESPONSE = "external_response"

    ALL = (
        USER_QUERY,
        DOCUMENT,
        METADATA,
        CONFIGURATION,
        FILE_PATH,
        URL,
        PROVIDER_MODEL,
        CONVERSATION_STATE,
        EXTERNAL_RESPONSE
    )

    @classmethod
    def is_valid(cls, boundary):
        return boundary in cls.ALL


class SecurityValidator:
    def __init__(
        self,
        logger,
        error_handler=None,
        policy=None
    ):
        if not isinstance(logger, Logger):
            raise ValueError(
                "Security validator logger must be a Logger"
            )

        if error_handler is not None:
            if not isinstance(error_handler, ErrorHandler):
                raise ValueError(
                    "Security validator error handler must be an ErrorHandler or None"
                )

        if policy is None:
            policy = SecurityPolicy()

        if not isinstance(policy, SecurityPolicy):
            raise ValueError(
                "Security validator policy must be a SecurityPolicy"
            )

        policy.validate()

        self.logger = logger
        self.error_handler = error_handler
        self.policy = policy
        self._trusted_boundaries = set()

    def _record_failure(
        self,
        message,
        field=None,
        exception_type=SecurityValidationError
    ):
        self.logger.error(
            f"Security validation rejected input: {message}"
        )

        if self.error_handler is not None:
            self.error_handler.handle_expected(
                message,
                category="validation",
                component="security",
                operation="validate",
                details={
                    "field": field,
                    "security_event": "validation_failure"
                }
            )

        return exception_type(
            message,
            field
        )

    def _build_result(
        self,
        value,
        errors=None,
        warnings=None
    ):
        return ValidationResult(
            valid=not errors,
            value=value,
            errors=errors or [],
            warnings=warnings or [],
            trusted=False
        )

    def validate_string(
        self,
        value,
        field="input",
        required=True,
        max_length=None
    ):
        if not isinstance(field, str) or not field.strip():
            raise ValueError(
                "Security validation field must be a non-empty string"
            )

        if not isinstance(value, str):
            error = self._record_failure(
                f"{field} must be a string",
                field
            )
            return self._build_result(
                value,
                [str(error)]
            )

        if required and not value.strip():
            error = self._record_failure(
                f"{field} cannot be empty",
                field
            )
            return self._build_result(
                value,
                [str(error)]
            )

        if max_length is None:
            max_length = self.policy.max_string_length

        if not isinstance(max_length, int) or max_length <= 0:
            raise ValueError(
                "Security string max length must be a positive integer"
            )

        if len(value) > max_length:
            error = self._record_failure(
                f"{field} exceeds the maximum allowed length",
                field
            )
            return self._build_result(
                value,
                [str(error)]
            )

        return self._build_result(value)

    def validate_mapping(
        self,
        value,
        field="input",
        required_fields=None,
        allowed_fields=None
    ):
        if not isinstance(value, dict):
            error = self._record_failure(
                f"{field} must be a dictionary",
                field
            )
            return self._build_result(
                value,
                [str(error)]
            )

        if len(value) > self.policy.max_metadata_size:
            error = self._record_failure(
                f"{field} exceeds the maximum allowed collection size",
                field
            )
            return self._build_result(
                value,
                [str(error)]
            )

        errors = []

        if required_fields is not None:
            if not isinstance(required_fields, (list, tuple, set)):
                raise ValueError(
                    "Security required fields must be a collection"
                )

            for required_field in required_fields:
                if required_field not in value:
                    errors.append(
                        f"{field} is missing required field: {required_field}"
                    )

        if allowed_fields is not None:
            if not isinstance(allowed_fields, (list, tuple, set)):
                raise ValueError(
                    "Security allowed fields must be a collection"
                )

            allowed_fields = set(allowed_fields)

            for key in value:
                if key not in allowed_fields:
                    errors.append(
                        f"{field} contains unexpected field: {key}"
                    )

        if errors:
            for message in errors:
                self._record_failure(
                    message,
                    field
                )

        return self._build_result(
            dict(value),
            errors
        )

    def validate_collection(
        self,
        value,
        field="input",
        max_size=None
    ):
        if not isinstance(value, (list, tuple, set)):
            error = self._record_failure(
                f"{field} must be a collection",
                field
            )
            return self._build_result(
                value,
                [str(error)]
            )

        if max_size is None:
            max_size = self.policy.max_collection_size

        if not isinstance(max_size, int) or max_size <= 0:
            raise ValueError(
                "Security collection max size must be a positive integer"
            )

        if len(value) > max_size:
            error = self._record_failure(
                f"{field} exceeds the maximum allowed collection size",
                field
            )
            return self._build_result(
                value,
                [str(error)]
            )

        return self._build_result(
            list(value)
        )

    def validate_input(
        self,
        value,
        field="input"
    ):
        if value is None:
            error = self._record_failure(
                f"{field} cannot be None",
                field
            )
            return self._build_result(
                value,
                [str(error)]
            )

        if isinstance(value, str):
            return self.validate_string(
                value,
                field
            )

        if isinstance(value, dict):
            return self.validate_mapping(
                value,
                field
            )

        if isinstance(value, (list, tuple, set)):
            return self.validate_collection(
                value,
                field
            )

        return self._build_result(
            value
        )

    def _validate_trust_boundary(
        self,
        boundary
    ):
        if not isinstance(boundary, str) or not boundary.strip():
            raise ValueError(
                "Security trust boundary must be a non-empty string"
            )
        if not TrustBoundary.is_valid(boundary):
            raise ValueError(
                f"Security trust boundary is not supported: {boundary}"
            )
        return boundary

    def validate_trust_boundary(
        self,
        value,
        boundary,
        field=None
    ):
        boundary = self._validate_trust_boundary(
            boundary
        )
        if field is None:
            field = boundary
        result = self.validate_input(
            value,
            field
        )
        result.boundary = boundary
        return result


    def require_valid(
        self,
        result,
        field="input"
    ):
        if not isinstance(result, ValidationResult):
            raise ValueError(
                "Security validation result must be a ValidationResult"
            )

        if not result.is_valid():
            message = (
                f"Security validation failed for {field}"
            )
            self.logger.error(message)

            if self.error_handler is not None:
                self.error_handler.handle_expected(
                    message,
                    category="validation",
                    component="security",
                    operation="require_valid",
                    details={
                        "field": field,
                        "security_event": "validation_rejection"
                    }
                )

            raise SecurityValidationError(
                message,
                field
            )

        return result.value

    def mark_trusted(
        self,
        result
    ):
        if not isinstance(result, ValidationResult):
            raise ValueError(
                "Security trust operation requires a ValidationResult"
            )

        if not result.is_valid():
            raise SecurityValidationError(
                "Invalid validation results cannot be trusted"
            )

        return ValidationResult(
            valid=True,
            value=result.value,
            errors=list(result.errors),
            warnings=list(result.warnings),
            trusted=True,
            boundary=result.boundary
        )

    def promote_boundary(
        self,
        result,
        boundary=None
    ):
        if not isinstance(result, ValidationResult):
            raise ValueError(
                "Security trust boundary promotion requires a ValidationResult"
            )
        if boundary is None:
            boundary = result.boundary
        boundary = self._validate_trust_boundary(
            boundary
        )
        if result.boundary is not None and result.boundary != boundary:
            raise SecurityValidationError(
                "Validation result does not belong to the requested trust boundary",
                result.boundary
            )
        if not result.is_valid():
            raise SecurityValidationError(
                "Invalid validation results cannot cross a trust boundary",
                result.boundary if result.boundary is not None else boundary
            )
        trusted_result = ValidationResult(
            valid=True,
            value=result.value,
            errors=list(result.errors),
            warnings=list(result.warnings),
            trusted=True,
            boundary=boundary
        )
        self._trusted_boundaries.add(
            boundary
        )
        self.logger.info(
            f"Security trust boundary promoted: {boundary}"
        )
        return trusted_result

    def validate_boundary_and_trust(
        self,
        value,
        boundary,
        field=None
    ):
        result = self.validate_trust_boundary(
            value,
            boundary,
            field
        )
        return self.promote_boundary(
            result,
            boundary
        )

    def is_boundary_trusted(
        self,
        boundary
    ):
        boundary = self._validate_trust_boundary(
            boundary
        )
        return boundary in self._trusted_boundaries

    def get_trust_boundaries(self):
        return list(TrustBoundary.ALL)

    def get_trusted_boundaries(self):
        return list(self._trusted_boundaries)


    def validate_and_trust(
        self,
        value,
        field="input"
    ):
        result = self.validate_input(
            value,
            field
        )
        return self.mark_trusted(
            result
        )

    def is_trusted(
        self,
        value
    ):
        if not isinstance(value, ValidationResult):
            return False
        return value.is_trusted()

    def get_policy(self):
        return self.policy.to_dict()

    def get_security_state(self):
        return {
            "secure_by_default": True,
            "policy": self.get_policy(),
            "logger_integrated": isinstance(
                self.logger,
                Logger
            ),
            "error_handler_integrated": (
                self.error_handler is not None
            ),
            "supported_trust_boundaries": self.get_trust_boundaries(),
            "trusted_boundaries": self.get_trusted_boundaries()
        }