from classes.logger import Logger
from classes.error_handler import ErrorHandler
import os
import tempfile
import unicodedata


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


class SecuritySchemaError(SecurityError):
    def __init__(self, message, field=None):
        super().__init__(message, category="schema")
        if field is not None and (not isinstance(field, str) or not field.strip()):
            raise ValueError("Security schema field must be a non-empty string or None")
        self.field = field


class SecuritySchema:
    def __init__(self, fields, allow_extra_fields=False):
        if not isinstance(fields, dict):
            raise ValueError("Security schema fields must be a dictionary")
        if not isinstance(allow_extra_fields, bool):
            raise ValueError("Security schema allow_extra_fields must be a boolean")
        self.fields = {}
        for name, definition in fields.items():
            if not isinstance(name, str) or not name.strip():
                raise ValueError("Security schema field names must be non-empty strings")
            if not isinstance(definition, dict):
                raise ValueError(f"Security schema definition for {name} must be a dictionary")
            item = dict(definition)
            field_type = item.get("type")
            if field_type is not None and not isinstance(field_type, type):
                raise ValueError(f"Security schema type for {name} must be a type or None")
            required = item.get("required", False)
            if not isinstance(required, bool):
                raise ValueError(f"Security schema required flag for {name} must be a boolean")
            if "allowed_values" in item:
                values = item["allowed_values"]
                if not isinstance(values, (list, tuple, set)) or not values:
                    raise ValueError(f"Security schema allowed values for {name} must be a non-empty collection")
                item["allowed_values"] = tuple(values)
            if item.get("schema") is not None and not isinstance(item["schema"], SecuritySchema):
                raise ValueError(f"Security nested schema for {name} must be a SecuritySchema")
            self.fields[name] = item
        self.allow_extra_fields = allow_extra_fields

    def to_dict(self):
        result = {}
        for name, definition in self.fields.items():
            item = dict(definition)
            if item.get("type") is not None:
                item["type"] = item["type"].__name__
            if "schema" in item and item["schema"] is not None:
                item["schema"] = item["schema"].to_dict()
            result[name] = item
        return {"fields": result, "allow_extra_fields": self.allow_extra_fields}


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
    DEFAULT_MAX_FIELD_LENGTH = 10000
    DEFAULT_MAX_DOCUMENT_SIZE = 1000000
    DEFAULT_MAX_QUERY_SIZE = 10000
    DEFAULT_MAX_CHUNK_SIZE = 100000
    DEFAULT_MAX_CONTEXT_SIZE = 500000
    DEFAULT_MAX_CONVERSATION_HISTORY_SIZE = 100000
    DEFAULT_ENCODING = "utf-8"
    DEFAULT_NORMALIZE_UNICODE = True
    DEFAULT_NORMALIZE_WHITESPACE = True
    DEFAULT_REJECT_CONTROL_CHARACTERS = True
    DEFAULT_REJECT_INVALID_CHARACTERS = True
    DEFAULT_REJECT_BINARY_CONTENT = True
    DEFAULT_REJECT_DANGEROUS_CONTENT = True
    DEFAULT_SECURE_TEMP_FILE_MODE = 0o600
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
        max_field_length=DEFAULT_MAX_FIELD_LENGTH,
        max_document_size=DEFAULT_MAX_DOCUMENT_SIZE,
        max_query_size=DEFAULT_MAX_QUERY_SIZE,
        max_chunk_size=DEFAULT_MAX_CHUNK_SIZE,
        max_context_size=DEFAULT_MAX_CONTEXT_SIZE,
        max_conversation_history_size=DEFAULT_MAX_CONVERSATION_HISTORY_SIZE,
        encoding=DEFAULT_ENCODING,
        normalize_unicode=DEFAULT_NORMALIZE_UNICODE,
        normalize_whitespace=DEFAULT_NORMALIZE_WHITESPACE,
        reject_control_characters=DEFAULT_REJECT_CONTROL_CHARACTERS,
        reject_invalid_characters=DEFAULT_REJECT_INVALID_CHARACTERS,
        reject_binary_content=DEFAULT_REJECT_BINARY_CONTENT,
        reject_dangerous_content=DEFAULT_REJECT_DANGEROUS_CONTENT,
        secure_temp_file_mode=DEFAULT_SECURE_TEMP_FILE_MODE,
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
        self.max_field_length = self._validate_positive_integer(
            max_field_length,
            "max field length"
        )
        self.max_document_size = self._validate_positive_integer(
            max_document_size,
            "max document size"
        )
        self.max_query_size = self._validate_positive_integer(
            max_query_size,
            "max query size"
        )
        self.max_chunk_size = self._validate_positive_integer(
            max_chunk_size,
            "max chunk size"
        )
        self.max_context_size = self._validate_positive_integer(
            max_context_size,
            "max context size"
        )
        self.max_conversation_history_size = self._validate_positive_integer(
            max_conversation_history_size,
            "max conversation history size"
        )
        if not isinstance(encoding, str) or not encoding.strip():
            raise ValueError(
                "Security encoding must be a non-empty string"
            )
        try:
            "".encode(encoding)
        except (LookupError, UnicodeError):
            raise ValueError(
                "Security encoding must be a supported encoding"
            )
        if not isinstance(normalize_unicode, bool):
            raise ValueError(
                "Security normalize_unicode must be a boolean"
            )
        if not isinstance(normalize_whitespace, bool):
            raise ValueError(
                "Security normalize_whitespace must be a boolean"
            )
        if not isinstance(reject_control_characters, bool):
            raise ValueError(
                "Security reject_control_characters must be a boolean"
            )
        if not isinstance(reject_invalid_characters, bool):
            raise ValueError(
                "Security reject_invalid_characters must be a boolean"
            )
        if not isinstance(reject_binary_content, bool):
            raise ValueError(
                "Security reject_binary_content must be a boolean"
            )
        if not isinstance(reject_dangerous_content, bool):
            raise ValueError(
                "Security reject_dangerous_content must be a boolean"
            )
        if not isinstance(secure_temp_file_mode, int) or isinstance(secure_temp_file_mode, bool):
            raise ValueError(
                "Security secure_temp_file_mode must be an integer"
            )
        if secure_temp_file_mode <= 0 or secure_temp_file_mode > 0o777:
            raise ValueError(
                "Security secure_temp_file_mode must be between 1 and 0o777"
            )
        self.encoding = encoding.strip().lower()
        self.normalize_unicode = normalize_unicode
        self.normalize_whitespace = normalize_whitespace
        self.reject_control_characters = reject_control_characters
        self.reject_invalid_characters = reject_invalid_characters
        self.reject_binary_content = reject_binary_content
        self.reject_dangerous_content = reject_dangerous_content
        self.secure_temp_file_mode = secure_temp_file_mode

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
        self._validate_positive_integer(
            self.max_field_length,
            "max field length"
        )
        self._validate_positive_integer(
            self.max_document_size,
            "max document size"
        )
        self._validate_positive_integer(
            self.max_query_size,
            "max query size"
        )
        self._validate_positive_integer(
            self.max_chunk_size,
            "max chunk size"
        )
        self._validate_positive_integer(
            self.max_context_size,
            "max context size"
        )
        self._validate_positive_integer(
            self.max_conversation_history_size,
            "max conversation history size"
        )
        if not isinstance(self.encoding, str) or not self.encoding.strip():
            raise ValueError(
                "Security encoding must be a non-empty string"
            )
        try:
            "".encode(self.encoding)
        except (LookupError, UnicodeError):
            raise ValueError(
                "Security encoding must be a supported encoding"
            )
        if not isinstance(self.normalize_unicode, bool):
            raise ValueError(
                "Security normalize_unicode must be a boolean"
            )
        if not isinstance(self.normalize_whitespace, bool):
            raise ValueError(
                "Security normalize_whitespace must be a boolean"
            )
        if not isinstance(self.reject_control_characters, bool):
            raise ValueError(
                "Security reject_control_characters must be a boolean"
            )
        if not isinstance(self.reject_invalid_characters, bool):
            raise ValueError(
                "Security reject_invalid_characters must be a boolean"
            )
        if not isinstance(self.reject_binary_content, bool):
            raise ValueError(
                "Security reject_binary_content must be a boolean"
            )
        if not isinstance(self.reject_dangerous_content, bool):
            raise ValueError(
                "Security reject_dangerous_content must be a boolean"
            )
        if not isinstance(self.secure_temp_file_mode, int) or isinstance(self.secure_temp_file_mode, bool):
            raise ValueError(
                "Security secure_temp_file_mode must be an integer"
            )
        if self.secure_temp_file_mode <= 0 or self.secure_temp_file_mode > 0o777:
            raise ValueError(
                "Security secure_temp_file_mode must be between 1 and 0o777"
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
            "max_field_length": self.max_field_length,
            "max_document_size": self.max_document_size,
            "max_query_size": self.max_query_size,
            "max_chunk_size": self.max_chunk_size,
            "max_context_size": self.max_context_size,
            "max_conversation_history_size": self.max_conversation_history_size,
            "encoding": self.encoding,
            "normalize_unicode": self.normalize_unicode,
            "normalize_whitespace": self.normalize_whitespace,
            "reject_control_characters": self.reject_control_characters,
            "reject_invalid_characters": self.reject_invalid_characters,
            "reject_binary_content": self.reject_binary_content,
            "reject_dangerous_content": self.reject_dangerous_content,
            "secure_temp_file_mode": self.secure_temp_file_mode,
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

    def validate_schema(
        self,
        value,
        schema,
        field="input",
        boundary=None
    ):
        if not isinstance(schema, SecuritySchema):
            raise ValueError(
                "Security schema validation requires a SecuritySchema"
            )
        if not isinstance(value, dict):
            error = self._record_failure(
                f"{field} must be a dictionary for schema validation",
                field,
                SecuritySchemaError
            )
            result = self._build_result(value, [str(error)])
            result.boundary = boundary
            return result
        errors = []
        for field_name, definition in schema.fields.items():
            required = definition.get("required", False)
            if required and field_name not in value:
                errors.append(f"{field} is missing required field: {field_name}")
                continue
            if field_name not in value:
                continue
            field_value = value[field_name]
            expected_type = definition.get("type")
            if expected_type is not None and not isinstance(field_value, expected_type):
                errors.append(f"{field}.{field_name} must be of type {expected_type.__name__}")
                continue
            allowed_values = definition.get("allowed_values")
            if allowed_values is not None and field_value not in allowed_values:
                errors.append(f"{field}.{field_name} contains a value outside the allowed values")
            nested_schema = definition.get("schema")
            if nested_schema is not None:
                nested_result = self.validate_schema(
                    field_value,
                    nested_schema,
                    f"{field}.{field_name}",
                    boundary
                )
                if nested_result.is_invalid():
                    errors.extend(nested_result.errors)
        if not schema.allow_extra_fields:
            for key in value:
                if key not in schema.fields:
                    errors.append(f"{field} contains unexpected field: {key}")
        if errors:
            for message in errors:
                self._record_failure(message, field, SecuritySchemaError)
        result = self._build_result(dict(value), errors)
        result.boundary = boundary
        return result

    def validate_typed_field(
        self,
        value,
        field,
        expected_type,
        allowed_values=None,
        required=True
    ):
        if not isinstance(field, str) or not field.strip():
            raise ValueError(
                "Security typed field name must be a non-empty string"
            )
        if not isinstance(expected_type, type):
            raise ValueError(
                "Security typed field expected type must be a type"
            )
        if not isinstance(required, bool):
            raise ValueError(
                "Security typed field required flag must be a boolean"
            )
        if allowed_values is not None:
            if not isinstance(allowed_values, (list, tuple, set)):
                raise ValueError(
                    "Security typed field allowed values must be a collection"
                )
            if not allowed_values:
                raise ValueError(
                    "Security typed field allowed values cannot be empty"
                )
        if value is None and not required:
            return self._build_result(value)
        if not isinstance(value, expected_type):
            error = self._record_failure(
                f"{field} must be of type {expected_type.__name__}",
                field,
                SecuritySchemaError
            )
            return self._build_result(value, [str(error)])
        if allowed_values is not None and value not in allowed_values:
            error = self._record_failure(
                f"{field} contains a value outside the allowed values",
                field,
                SecuritySchemaError
            )
            return self._build_result(value, [str(error)])
        return self._build_result(value)

    def validate_size_limit(
        self,
        value,
        limit,
        field="input",
        unit="characters"
    ):
        if not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
            raise ValueError(
                "Security size limit must be a positive integer"
            )
        if not isinstance(field, str) or not field.strip():
            raise ValueError(
                "Security size limit field must be a non-empty string"
            )
        if not isinstance(unit, str) or not unit.strip():
            raise ValueError(
                "Security size limit unit must be a non-empty string"
            )
        if isinstance(value, str):
            size = len(value)
        elif isinstance(value, (list, tuple, set, dict)):
            size = len(value)
        else:
            raise ValueError(
                "Security size validation requires a string or collection"
            )
        if size > limit:
            error = self._record_failure(
                f"{field} exceeds the maximum allowed {unit}",
                field
            )
            return self._build_result(
                value,
                [str(error)]
            )
        return self._build_result(
            value
        )

    def validate_field_length(
        self,
        value,
        field="input"
    ):
        return self.validate_size_limit(
            value,
            self.policy.max_field_length,
            field,
            "field length"
        )

    def validate_document_size(
        self,
        value,
        field="document"
    ):
        return self.validate_size_limit(
            value,
            self.policy.max_document_size,
            field,
            "document size"
        )

    def validate_query_size(
        self,
        value,
        field="query"
    ):
        return self.validate_size_limit(
            value,
            self.policy.max_query_size,
            field,
            "query size"
        )

    def validate_chunk_size(
        self,
        value,
        field="chunk"
    ):
        return self.validate_size_limit(
            value,
            self.policy.max_chunk_size,
            field,
            "chunk size"
        )

    def validate_context_size(
        self,
        value,
        field="context"
    ):
        return self.validate_size_limit(
            value,
            self.policy.max_context_size,
            field,
            "context size"
        )

    def validate_conversation_history_size(
        self,
        value,
        field="conversation_history"
    ):
        return self.validate_size_limit(
            value,
            self.policy.max_conversation_history_size,
            field,
            "conversation history size"
        )

    def validate_complexity(
        self,
        value,
        field="input",
        max_depth=None,
        max_collection_size=None
    ):
        if max_depth is None:
            max_depth = self.policy.max_nesting_depth
        if max_collection_size is None:
            max_collection_size = self.policy.max_collection_size
        if not isinstance(max_depth, int) or isinstance(max_depth, bool) or max_depth <= 0:
            raise ValueError(
                "Security complexity max depth must be a positive integer"
            )
        if not isinstance(max_collection_size, int) or isinstance(max_collection_size, bool) or max_collection_size <= 0:
            raise ValueError(
                "Security complexity max collection size must be a positive integer"
            )

        def depth(item, current_depth=0):
            if isinstance(item, dict):
                if len(item) > max_collection_size:
                    return current_depth + 1, True
                if not item:
                    return current_depth + 1, False
                children = [
                    depth(child, current_depth + 1)
                    for child in item.values()
                ]
            elif isinstance(item, (list, tuple, set)):
                if len(item) > max_collection_size:
                    return current_depth + 1, True
                if not item:
                    return current_depth + 1, False
                children = [
                    depth(child, current_depth + 1)
                    for child in item
                ]
            else:
                return current_depth, False
            maximum_depth = max(item_depth for item_depth, _ in children)
            oversized = any(item_oversized for _, item_oversized in children)
            return maximum_depth, oversized

        current_depth, oversized_collection = depth(value)
        errors = []
        if current_depth > max_depth:
            errors.append(
                f"{field} exceeds the maximum allowed nesting depth"
            )
        if oversized_collection:
            errors.append(
                f"{field} contains a collection exceeding the maximum allowed collection size"
            )
        if errors:
            for message in errors:
                self._record_failure(
                    message,
                    field
                )
        return self._build_result(
            value,
            errors
        )


    def validate_encoding(
        self,
        value,
        field="input",
        encoding=None
    ):
        if not isinstance(value, str):
            error = self._record_failure(
                f"{field} must be a string for encoding validation",
                field
            )
            return self._build_result(
                value,
                [str(error)]
            )
        if encoding is None:
            encoding = self.policy.encoding
        if not isinstance(encoding, str) or not encoding.strip():
            raise ValueError(
                "Security encoding must be a non-empty string"
            )
        try:
            encoded = value.encode(
                encoding
            )
            decoded = encoded.decode(
                encoding
            )
        except (LookupError, UnicodeError):
            error = self._record_failure(
                f"{field} contains invalid data for encoding {encoding}",
                field
            )
            return self._build_result(
                value,
                [str(error)]
            )
        if self.policy.reject_invalid_characters and decoded != value:
            error = self._record_failure(
                f"{field} failed encoding round-trip validation",
                field
            )
            return self._build_result(
                value,
                [str(error)]
            )
        return self._build_result(
            decoded
        )

    def normalize_input(
        self,
        value,
        field="input"
    ):
        if not isinstance(value, str):
            error = self._record_failure(
                f"{field} must be a string for normalization",
                field
            )
            return self._build_result(
                value,
                [str(error)]
            )
        if self.policy.reject_control_characters:
            for character in value:
                if unicodedata.category(character) == "Cc":
                    error = self._record_failure(
                        f"{field} contains control characters",
                        field
                    )
                    return self._build_result(
                        value,
                        [str(error)]
                    )
        if self.policy.reject_invalid_characters:
            for character in value:
                if unicodedata.category(character) == "Cs":
                    error = self._record_failure(
                        f"{field} contains invalid Unicode characters",
                        field
                    )
                    return self._build_result(
                        value,
                        [str(error)]
                    )
        normalized = value
        if self.policy.normalize_unicode:
            normalized = unicodedata.normalize(
                "NFC",
                normalized
            )
        if self.policy.normalize_whitespace:
            normalized = " ".join(
                normalized.split()
            )
        return self._build_result(
            normalized
        )

    def validate_and_normalize(
        self,
        value,
        field="input"
    ):
        validation = self.validate_string(
            value,
            field
        )
        if validation.is_invalid():
            return validation
        return self.normalize_input(
            validation.value,
            field
        )

    def validate_normalization_order(
        self,
        value,
        field="input"
    ):
        encoded = self.validate_encoding(
            value,
            field
        )
        if encoded.is_invalid():
            return encoded
        normalized = self.normalize_input(
            encoded.value,
            field
        )
        if normalized.is_invalid():
            return normalized
        return self.validate_string(
            normalized.value,
            field
        )


    def validate_file_extension(
        self,
        file_name,
        field="file"
    ):
        if not isinstance(file_name, str) or not file_name.strip():
            error = self._record_failure(
                f"{field} must be a non-empty file name",
                field
            )
            return self._build_result(
                file_name,
                [str(error)]
            )
        extension = os.path.splitext(
            file_name
        )[1].lower()
        if extension not in self.policy.allowed_file_types:
            error = self._record_failure(
                f"{field} has an unsupported file type: {extension or 'none'}",
                field
            )
            return self._build_result(
                file_name,
                [str(error)]
            )
        return self._build_result(
            file_name
        )

    def validate_file_size(
        self,
        file_size,
        field="file"
    ):
        if not isinstance(file_size, int) or isinstance(file_size, bool):
            error = self._record_failure(
                f"{field} size must be an integer",
                field
            )
            return self._build_result(
                file_size,
                [str(error)]
            )
        if file_size < 0:
            error = self._record_failure(
                f"{field} size cannot be negative",
                field
            )
            return self._build_result(
                file_size,
                [str(error)]
            )
        if file_size > self.policy.max_document_size:
            error = self._record_failure(
                f"{field} exceeds the maximum allowed file size",
                field
            )
            return self._build_result(
                file_size,
                [str(error)]
            )
        return self._build_result(
            file_size
        )

    def validate_file_content(
        self,
        content,
        file_name,
        field="file"
    ):
        extension_result = self.validate_file_extension(
            file_name,
            field
        )
        if extension_result.is_invalid():
            return extension_result
        if isinstance(content, bytes):
            if not content:
                error = self._record_failure(
                    f"{field} cannot be empty",
                    field
                )
                return self._build_result(
                    content,
                    [str(error)]
                )
            if len(content) > self.policy.max_document_size:
                error = self._record_failure(
                    f"{field} exceeds the maximum allowed file size",
                    field
                )
                return self._build_result(
                    content,
                    [str(error)]
                )
            if self.policy.reject_binary_content and b"\x00" in content:
                error = self._record_failure(
                    f"{field} contains binary content",
                    field
                )
                return self._build_result(
                    content,
                    [str(error)]
                )
            try:
                decoded = content.decode(
                    self.policy.encoding
                )
            except (UnicodeDecodeError, LookupError):
                error = self._record_failure(
                    f"{field} contains malformed content for {self.policy.encoding}",
                    field
                )
                return self._build_result(
                    content,
                    [str(error)]
                )
        elif isinstance(content, str):
            if not content:
                error = self._record_failure(
                    f"{field} cannot be empty",
                    field
                )
                return self._build_result(
                    content,
                    [str(error)]
                )
            if len(content.encode(self.policy.encoding)) > self.policy.max_document_size:
                error = self._record_failure(
                    f"{field} exceeds the maximum allowed file size",
                    field
                )
                return self._build_result(
                    content,
                    [str(error)]
                )
            decoded = content
        else:
            error = self._record_failure(
                f"{field} content must be bytes or string data",
                field
            )
            return self._build_result(
                content,
                [str(error)]
            )
        if self.policy.reject_dangerous_content:
            dangerous_markers = (
                "\x00",
                "#!/bin/",
                "<script",
                "<?php"
            )
            lowered = decoded.lower()
            for marker in dangerous_markers:
                if marker in lowered:
                    error = self._record_failure(
                        f"{field} contains potentially dangerous content",
                        field
                    )
                    return self._build_result(
                        content,
                        [str(error)]
                    )
        normalized_result = self.normalize_input(
            decoded,
            field
        )
        if normalized_result.is_invalid():
            return self._build_result(
                content,
                normalized_result.errors
            )
        return self._build_result(
            normalized_result.value
        )

    def validate_document_file(
        self,
        file_name,
        content,
        field="document"
    ):
        return self.validate_file_content(
            content,
            file_name,
            field
        )

    def validate_file(
        self,
        file_path,
        field="file"
    ):
        if not isinstance(file_path, str) or not file_path.strip():
            error = self._record_failure(
                f"{field} path must be a non-empty string",
                field
            )
            return self._build_result(
                file_path,
                [str(error)]
            )
        extension_result = self.validate_file_extension(
            file_path,
            field
        )
        if extension_result.is_invalid():
            return extension_result
        try:
            file_size = os.path.getsize(
                file_path
            )
        except (OSError, ValueError) as exception:
            error = self._record_failure(
                f"{field} could not be inspected: {exception}",
                field
            )
            return self._build_result(
                file_path,
                [str(error)]
            )
        size_result = self.validate_file_size(
            file_size,
            field
        )
        if size_result.is_invalid():
            return size_result
        try:
            with open(
                file_path,
                "rb"
            ) as file_handle:
                content = file_handle.read(
                    self.policy.max_document_size + 1
                )
        except (OSError, ValueError) as exception:
            error = self._record_failure(
                f"{field} could not be read: {exception}",
                field
            )
            return self._build_result(
                file_path,
                [str(error)]
            )
        content_result = self.validate_file_content(
            content,
            file_path,
            field
        )
        if content_result.is_invalid():
            return self._build_result(
                file_path,
                content_result.errors
            )
        return self._build_result(
            {
                "path": file_path,
                "size": file_size,
                "content": content_result.value
            }
        )

    def create_secure_temp_file(
        self,
        suffix=".txt",
        field="temporary_file"
    ):
        extension_result = self.validate_file_extension(
            f"temporary{suffix}",
            field
        )
        if extension_result.is_invalid():
            raise SecurityValidationError(
                "Security temporary file type is not allowed",
                field
            )
        file_descriptor, file_path = tempfile.mkstemp(
            suffix=suffix
        )
        try:
            os.chmod(
                file_path,
                self.policy.secure_temp_file_mode
            )
        except OSError:
            os.close(
                file_descriptor
            )
            try:
                os.remove(
                    file_path
                )
            except OSError:
                pass
            raise SecurityValidationError(
                "Security temporary file permissions could not be secured",
                field
            )
        os.close(
            file_descriptor
        )
        self.logger.info(
            "Security secure temporary file created"
        )
        return file_path

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