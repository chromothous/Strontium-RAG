from classes.logger import Logger
from classes.error_handler import ErrorHandler
import os
import tempfile
import unicodedata
import ipaddress
from urllib.parse import urlparse
from pathlib import Path


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


class SecurityContentError(SecurityError):
    def __init__(
        self,
        message,
        field=None,
        source=None
    ):
        super().__init__(
            message,
            category="content"
        )
        if field is not None:
            if not isinstance(field, str) or not field.strip():
                raise ValueError(
                    "Security content field must be a non-empty string or None"
                )
        if source is not None:
            if not isinstance(source, str) or not source.strip():
                raise ValueError(
                    "Security content source must be a non-empty string or None"
                )
            if source not in SecurityContentSource.ALL:
                raise ValueError(
                    f"Security content source is not supported: {source}"
                )
        self.field = field
        self.source = source


class SecurityContentSource:
    SYSTEM = "system"
    USER = "user"
    RETRIEVED = "retrieved"
    EXTERNAL = "external"

    ALL = (
        SYSTEM,
        USER,
        RETRIEVED,
        EXTERNAL
    )

    TRUSTED = (
        SYSTEM,
    )

    UNTRUSTED = (
        USER,
        RETRIEVED,
        EXTERNAL
    )

    @classmethod
    def is_valid(cls, source):
        return source in cls.ALL

    @classmethod
    def is_trusted_source(cls, source):
        return source in cls.TRUSTED

    @classmethod
    def is_untrusted_source(cls, source):
        return source in cls.UNTRUSTED


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
        boundary=None,
        source=None,
        instructions_detected=False,
        commands_detected=False
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
        if source is not None:
            if not isinstance(source, str) or not source.strip():
                raise ValueError(
                    "Validation result source must be a non-empty string or None"
                )
            if not SecurityContentSource.is_valid(source):
                raise ValueError(
                    f"Validation result source is not supported: {source}"
                )
        if not isinstance(instructions_detected, bool):
            raise ValueError(
                "Validation result instructions_detected flag must be a boolean"
            )
        if not isinstance(commands_detected, bool):
            raise ValueError(
                "Validation result commands_detected flag must be a boolean"
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
        self.source = source
        self.instructions_detected = instructions_detected
        self.commands_detected = commands_detected

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
            "boundary": self.boundary,
            "source": self.source,
            "instructions_detected": self.instructions_detected,
            "commands_detected": self.commands_detected
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
    DEFAULT_ALLOW_RELATIVE_PATHS = False
    DEFAULT_REJECT_PARENT_TRAVERSAL = True
    DEFAULT_REJECT_SYMLINKS = True
    DEFAULT_ALLOWED_PATH_ROOTS = ()
    DEFAULT_PROTECTED_PATHS = ()
    DEFAULT_BLOCK_LOCAL_ADDRESSES = True
    DEFAULT_ALLOW_URL_CREDENTIALS = False
    DEFAULT_ALLOWED_HOSTS = ()
    DEFAULT_BLOCKED_HOSTS = ()
    DEFAULT_REJECT_SUSPICIOUS_INSTRUCTIONS = True
    DEFAULT_REJECT_EMBEDDED_COMMANDS = True
    DEFAULT_ALLOWED_CONTENT_SOURCES = (
        "system",
        "user",
        "retrieved",
        "external",
    )
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
        allow_relative_paths=DEFAULT_ALLOW_RELATIVE_PATHS,
        reject_parent_traversal=DEFAULT_REJECT_PARENT_TRAVERSAL,
        reject_symlinks=DEFAULT_REJECT_SYMLINKS,
        allowed_path_roots=None,
        protected_paths=None,
        block_local_addresses=DEFAULT_BLOCK_LOCAL_ADDRESSES,
        allow_url_credentials=DEFAULT_ALLOW_URL_CREDENTIALS,
        allowed_hosts=None,
        blocked_hosts=None,
        reject_suspicious_instructions=DEFAULT_REJECT_SUSPICIOUS_INSTRUCTIONS,
        reject_embedded_commands=DEFAULT_REJECT_EMBEDDED_COMMANDS,
        allowed_content_sources=DEFAULT_ALLOWED_CONTENT_SOURCES,
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
        if not isinstance(allow_relative_paths, bool):
            raise ValueError(
                "Security allow_relative_paths must be a boolean"
            )
        if not isinstance(reject_parent_traversal, bool):
            raise ValueError(
                "Security reject_parent_traversal must be a boolean"
            )
        if not isinstance(reject_symlinks, bool):
            raise ValueError(
                "Security reject_symlinks must be a boolean"
            )
        if allowed_path_roots is None:
            allowed_path_roots = self.DEFAULT_ALLOWED_PATH_ROOTS
        if protected_paths is None:
            protected_paths = self.DEFAULT_PROTECTED_PATHS
        if not isinstance(allowed_path_roots, (list, tuple)):
            raise ValueError(
                "Security allowed path roots must be a list or tuple"
            )
        if not isinstance(protected_paths, (list, tuple)):
            raise ValueError(
                "Security protected paths must be a list or tuple"
            )
        normalized_roots = []
        for root in allowed_path_roots:
            if not isinstance(root, str) or not root.strip():
                raise ValueError(
                    "Security allowed path roots must contain non-empty strings"
                )
            normalized_roots.append(
                str(
                    Path(root).expanduser().resolve(strict=False)
                )
            )
        normalized_protected = []
        for protected in protected_paths:
            if not isinstance(protected, str) or not protected.strip():
                raise ValueError(
                    "Security protected paths must contain non-empty strings"
                )
            normalized_protected.append(
                str(
                    Path(protected).expanduser().resolve(strict=False)
                )
            )
        self.encoding = encoding.strip().lower()
        self.normalize_unicode = normalize_unicode
        self.normalize_whitespace = normalize_whitespace
        self.reject_control_characters = reject_control_characters
        self.reject_invalid_characters = reject_invalid_characters
        self.reject_binary_content = reject_binary_content
        self.reject_dangerous_content = reject_dangerous_content
        self.secure_temp_file_mode = secure_temp_file_mode
        self.allow_relative_paths = allow_relative_paths
        self.reject_parent_traversal = reject_parent_traversal
        self.reject_symlinks = reject_symlinks
        self.allowed_path_roots = tuple(
            normalized_roots
        )
        self.protected_paths = tuple(
            normalized_protected
        )
        if not isinstance(block_local_addresses, bool):
            raise ValueError(
                "Security block_local_addresses must be a boolean"
            )
        if not isinstance(allow_url_credentials, bool):
            raise ValueError(
                "Security allow_url_credentials must be a boolean"
            )
        if allowed_hosts is None:
            allowed_hosts = ()
        if blocked_hosts is None:
            blocked_hosts = ()
        if not isinstance(allowed_hosts, (list, tuple)):
            raise ValueError(
                "Security allowed hosts must be a list or tuple"
            )
        if not isinstance(blocked_hosts, (list, tuple)):
            raise ValueError(
                "Security blocked hosts must be a list or tuple"
            )
        normalized_allowed_hosts = []
        for host in allowed_hosts:
            if not isinstance(host, str) or not host.strip():
                raise ValueError(
                    "Security allowed hosts must contain non-empty strings"
                )
            normalized_allowed_hosts.append(
                host.strip().lower().rstrip(".")
            )
        normalized_blocked_hosts = []
        for host in blocked_hosts:
            if not isinstance(host, str) or not host.strip():
                raise ValueError(
                    "Security blocked hosts must contain non-empty strings"
                )
            normalized_blocked_hosts.append(
                host.strip().lower().rstrip(".")
            )
        self.block_local_addresses = block_local_addresses
        self.allow_url_credentials = allow_url_credentials
        self.allowed_hosts = tuple(
            normalized_allowed_hosts
        )
        self.blocked_hosts = tuple(
            normalized_blocked_hosts
        )
        if not isinstance(reject_suspicious_instructions, bool):
            raise ValueError(
                "Security reject_suspicious_instructions must be a boolean"
            )
        if not isinstance(reject_embedded_commands, bool):
            raise ValueError(
                "Security reject_embedded_commands must be a boolean"
            )
        if not isinstance(allowed_content_sources, (list, tuple)):
            raise ValueError(
                "Security allowed content sources must be a list or tuple"
            )
        if not allowed_content_sources:
            raise ValueError(
                "Security allowed content sources cannot be empty"
            )
        normalized_content_sources = []
        for content_source in allowed_content_sources:
            if not isinstance(content_source, str) or not content_source.strip():
                raise ValueError(
                    "Security content sources must contain non-empty strings"
                )
            if content_source not in SecurityContentSource.ALL:
                raise ValueError(
                    f"Security content source is not supported: {content_source}"
                )
            normalized_content_sources.append(
                content_source
            )
        self.reject_suspicious_instructions = reject_suspicious_instructions
        self.reject_embedded_commands = reject_embedded_commands
        self.allowed_content_sources = tuple(
            normalized_content_sources
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
        if not isinstance(self.allow_relative_paths, bool):
            raise ValueError(
                "Security allow_relative_paths must be a boolean"
            )
        if not isinstance(self.reject_parent_traversal, bool):
            raise ValueError(
                "Security reject_parent_traversal must be a boolean"
            )
        if not isinstance(self.reject_symlinks, bool):
            raise ValueError(
                "Security reject_symlinks must be a boolean"
            )
        if not isinstance(self.allowed_path_roots, tuple):
            raise ValueError(
                "Security allowed path roots must be a tuple"
            )
        if not isinstance(self.protected_paths, tuple):
            raise ValueError(
                "Security protected paths must be a tuple"
            )
        if not isinstance(self.block_local_addresses, bool):
            raise ValueError(
                "Security block_local_addresses must be a boolean"
            )
        if not isinstance(self.allow_url_credentials, bool):
            raise ValueError(
                "Security allow_url_credentials must be a boolean"
            )
        if not isinstance(self.allowed_hosts, tuple):
            raise ValueError(
                "Security allowed hosts must be a tuple"
            )
        if not isinstance(self.blocked_hosts, tuple):
            raise ValueError(
                "Security blocked hosts must be a tuple"
            )
        if not isinstance(self.reject_suspicious_instructions, bool):
            raise ValueError(
                "Security reject_suspicious_instructions must be a boolean"
            )
        if not isinstance(self.reject_embedded_commands, bool):
            raise ValueError(
                "Security reject_embedded_commands must be a boolean"
            )
        if not isinstance(self.allowed_content_sources, tuple):
            raise ValueError(
                "Security allowed content sources must be a tuple"
            )
        if not self.allowed_content_sources:
            raise ValueError(
                "Security allowed content sources cannot be empty"
            )
        for content_source in self.allowed_content_sources:
            if not SecurityContentSource.is_valid(content_source):
                raise ValueError(
                    f"Security content source is not supported: {content_source}"
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
            "allow_relative_paths": self.allow_relative_paths,
            "reject_parent_traversal": self.reject_parent_traversal,
            "reject_symlinks": self.reject_symlinks,
            "allowed_path_roots": tuple(
                self.allowed_path_roots
            ),
            "protected_paths": tuple(
                self.protected_paths
            ),
            "block_local_addresses": self.block_local_addresses,
            "allow_url_credentials": self.allow_url_credentials,
            "allowed_hosts": tuple(
                self.allowed_hosts
            ),
            "blocked_hosts": tuple(
                self.blocked_hosts
            ),
            "reject_suspicious_instructions": self.reject_suspicious_instructions,
            "reject_embedded_commands": self.reject_embedded_commands,
            "allowed_content_sources": tuple(
                self.allowed_content_sources
            ),
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
            boundary=result.boundary,
            source=result.source,
            instructions_detected=result.instructions_detected,
            commands_detected=result.commands_detected
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
            boundary=boundary,
            source=result.source,
            instructions_detected=result.instructions_detected,
            commands_detected=result.commands_detected
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
        path_result = self.validate_safe_file_path(
            file_path,
            field
        )
        if path_result.is_invalid():
            return path_result
        file_path = path_result.value
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

    def _path_contains_symlink(
        self,
        path
    ):
        path = Path(path)
        if not path.is_absolute():
            path = Path.cwd() / path
        current = Path(path.anchor)
        for part in path.parts:
            if part == path.anchor:
                continue
            current = current / part
            try:
                if current.is_symlink():
                    return True
            except OSError:
                return True
        return False

    def _is_path_within_root(
        self,
        path,
        root
    ):
        try:
            Path(path).relative_to(
                Path(root)
            )
            return True
        except ValueError:
            return False

    def _is_protected_path(
        self,
        path
    ):
        for protected in self.policy.protected_paths:
            if self._is_path_within_root(
                path,
                protected
            ):
                return True
        return False

    def _contains_parent_traversal(
        self,
        path
    ):
        normalized = path.replace(
            "\\",
            "/"
        )
        return ".." in normalized.split("/")

    def validate_path(
        self,
        path,
        field="file_path",
        must_exist=False,
        allow_directory=False
    ):
        if not isinstance(path, str) or not path.strip():
            error = self._record_failure(
                f"{field} must be a non-empty path string",
                field
            )
            return self._build_result(
                path,
                [str(error)]
            )
        if "\x00" in path:
            error = self._record_failure(
                f"{field} contains a null byte",
                field
            )
            return self._build_result(
                path,
                [str(error)]
            )
        if (
            self.policy.reject_parent_traversal
            and self._contains_parent_traversal(path)
        ):
            error = self._record_failure(
                f"{field} contains parent traversal",
                field
            )
            return self._build_result(
                path,
                [str(error)]
            )
        raw_path = Path(
            path
        ).expanduser()
        if not raw_path.is_absolute():
            if not self.policy.allow_relative_paths:
                error = self._record_failure(
                    f"{field} must be an absolute path",
                    field
                )
                return self._build_result(
                    path,
                    [str(error)]
                )
            raw_path = Path.cwd() / raw_path
        normalized_path = Path(
            os.path.abspath(
                os.path.normpath(
                    str(raw_path)
                )
            )
        )
        if (
            self.policy.reject_symlinks
            and self._path_contains_symlink(normalized_path)
        ):
            error = self._record_failure(
                f"{field} contains a symbolic link",
                field
            )
            return self._build_result(
                path,
                [str(error)]
            )
        resolved_path = normalized_path.resolve(
            strict=False
        )
        if self._is_protected_path(
            resolved_path
        ):
            error = self._record_failure(
                f"{field} targets a protected path",
                field
            )
            return self._build_result(
                path,
                [str(error)]
            )
        if self.policy.allowed_path_roots:
            allowed = any(
                self._is_path_within_root(
                    resolved_path,
                    root
                )
                for root in self.policy.allowed_path_roots
            )
            if not allowed:
                error = self._record_failure(
                    f"{field} is outside the allowed path roots",
                    field
                )
                return self._build_result(
                    path,
                    [str(error)]
                )
        exists = resolved_path.exists()
        if must_exist and not exists:
            error = self._record_failure(
                f"{field} does not exist",
                field
            )
            return self._build_result(
                path,
                [str(error)]
            )
        if (
            exists
            and not allow_directory
            and resolved_path.is_dir()
        ):
            error = self._record_failure(
                f"{field} must reference a file",
                field
            )
            return self._build_result(
                path,
                [str(error)]
            )
        return self._build_result(
            str(resolved_path)
        )

    def validate_file_path(
        self,
        path,
        field="file_path",
        must_exist=False
    ):
        result = self.validate_path(
            path,
            field,
            must_exist=must_exist,
            allow_directory=False
        )
        if result.is_invalid():
            return result
        extension_result = self.validate_file_extension(
            result.value,
            field
        )
        if extension_result.is_invalid():
            return extension_result
        return result

    def validate_directory_path(
        self,
        path,
        field="directory",
        must_exist=False
    ):
        return self.validate_path(
            path,
            field,
            must_exist=must_exist,
            allow_directory=True
        )

    def validate_safe_file_path(
        self,
        path,
        field="file_path"
    ):
        return self.validate_file_path(
            path,
            field,
            must_exist=True
        )

    def _normalize_url_host(
        self,
        host
    ):
        if host is None:
            return None
        return host.strip().lower().rstrip(".")

    def _host_is_local_or_internal(
        self,
        host
    ):
        normalized_host = self._normalize_url_host(
            host
        )
        if not normalized_host:
            return True
        local_hostnames = {
            "localhost",
            "localhost.localdomain",
            "ip6-localhost",
            "ip6-loopback"
        }
        if normalized_host in local_hostnames:
            return True
        if (
            normalized_host.endswith(".localhost")
            or normalized_host.endswith(".local")
            or normalized_host.endswith(".internal")
            or normalized_host.endswith(".lan")
        ):
            return True
        try:
            address = ipaddress.ip_address(
                normalized_host
            )
        except ValueError:
            return False
        return (
            address.is_loopback
            or address.is_private
            or address.is_link_local
            or address.is_unspecified
            or address.is_reserved
            or address.is_multicast
        )

    def _host_allowed_by_policy(
        self,
        host
    ):
        normalized_host = self._normalize_url_host(
            host
        )
        if normalized_host in self.policy.blocked_hosts:
            return False
        if self.policy.allowed_hosts:
            return normalized_host in self.policy.allowed_hosts
        return True

    def validate_url(
        self,
        url,
        field="url",
        require_external=True
    ):
        if not isinstance(url, str) or not url.strip():
            error = self._record_failure(
                f"{field} must be a non-empty URL",
                field
            )
            return self._build_result(
                url,
                [str(error)]
            )
        if len(url) > self.policy.max_string_length:
            error = self._record_failure(
                f"{field} exceeds the maximum allowed length",
                field
            )
            return self._build_result(
                url,
                [str(error)]
            )
        try:
            parsed = urlparse(
                url.strip()
            )
            scheme = parsed.scheme.lower()
            hostname = parsed.hostname
            port = parsed.port
        except ValueError as exception:
            error = self._record_failure(
                f"{field} is malformed: {exception}",
                field
            )
            return self._build_result(
                url,
                [str(error)]
            )
        if not scheme:
            error = self._record_failure(
                f"{field} must include a URL scheme",
                field
            )
            return self._build_result(
                url,
                [str(error)]
            )
        if scheme not in self.policy.allowed_schemes:
            error = self._record_failure(
                f"{field} uses a disallowed URL scheme",
                field
            )
            return self._build_result(
                url,
                [str(error)]
            )
        if hostname is None or not hostname.strip():
            error = self._record_failure(
                f"{field} must include a hostname",
                field
            )
            return self._build_result(
                url,
                [str(error)]
            )
        if not self.policy.allow_url_credentials and (
            parsed.username is not None
            or parsed.password is not None
        ):
            error = self._record_failure(
                f"{field} cannot include URL credentials",
                field
            )
            return self._build_result(
                url,
                [str(error)]
            )
        normalized_host = self._normalize_url_host(
            hostname
        )
        if require_external and (
            self.policy.block_local_addresses
            and self._host_is_local_or_internal(normalized_host)
        ):
            error = self._record_failure(
                f"{field} targets a local or internal address",
                field
            )
            return self._build_result(
                url,
                [str(error)]
            )
        if not self._host_allowed_by_policy(
            normalized_host
        ):
            error = self._record_failure(
                f"{field} host is restricted by security policy",
                field
            )
            return self._build_result(
                url,
                [str(error)]
            )
        if port is not None and (
            port <= 0
            or port > 65535
        ):
            error = self._record_failure(
                f"{field} contains an invalid port",
                field
            )
            return self._build_result(
                url,
                [str(error)]
            )
        return self._build_result(
            url.strip()
        )

    def validate_external_resource(
        self,
        url,
        field="external_resource"
    ):
        result = self.validate_url(
            url,
            field,
            require_external=True
        )
        result.boundary = TrustBoundary.URL
        return result

    def validate_provider_endpoint(
        self,
        url,
        field="provider_endpoint"
    ):
        result = self.validate_url(
            url,
            field,
            require_external=True
        )
        result.boundary = TrustBoundary.PROVIDER_MODEL
        return result

    def validate_redirect_target(
        self,
        target_url,
        source_url=None,
        field="redirect"
    ):
        target_result = self.validate_url(
            target_url,
            field,
            require_external=True
        )
        if target_result.is_invalid():
            return target_result
        if source_url is not None:
            source_result = self.validate_url(
                source_url,
                f"{field}_source",
                require_external=True
            )
            if source_result.is_invalid():
                return self._build_result(
                    target_url,
                    source_result.errors
                )
            source_parsed = urlparse(
                source_result.value
            )
            target_parsed = urlparse(
                target_result.value
            )
            if source_parsed.scheme.lower() == "https" and target_parsed.scheme.lower() != "https":
                error = self._record_failure(
                    f"{field} cannot downgrade from HTTPS",
                    field
                )
                return self._build_result(
                    target_url,
                    [str(error)]
                )
        target_result.boundary = TrustBoundary.URL
        return target_result

    def _validate_content_source(
        self,
        source
    ):
        if not isinstance(source, str) or not source.strip():
            raise ValueError(
                "Security content source must be a non-empty string"
            )
        if not SecurityContentSource.is_valid(source):
            raise ValueError(
                f"Security content source is not supported: {source}"
            )
        if source not in self.policy.allowed_content_sources:
            raise SecurityContentError(
                "Security content source is disabled by policy",
                source
            )
        return source

    def _find_suspicious_instruction_markers(
        self,
        content
    ):
        lowered = content.lower()
        markers = (
            "ignore previous instructions",
            "ignore all previous instructions",
            "disregard previous instructions",
            "disregard all previous instructions",
            "forget previous instructions",
            "override system instructions",
            "override the system",
            "reveal the system prompt",
            "show the system prompt",
            "system prompt",
            "developer message",
            "follow these instructions instead",
            "do not follow the previous",
            "jailbreak",
            "prompt injection"
        )
        return tuple(
            marker
            for marker in markers
            if marker in lowered
        )

    def _find_embedded_command_markers(
        self,
        content
    ):
        lowered = content.lower()
        markers = (
            "#!/bin/",
            "powershell -",
            "cmd.exe",
            "invoke-expression",
            "os.system(",
            "subprocess.",
            "curl ",
            "wget ",
            "curl|",
            "wget|",
            "rm -rf ",
            "javascript:",
            "<script",
            "<?php"
        )
        return tuple(
            marker
            for marker in markers
            if marker in lowered
        )

    def is_content_source_trusted(
        self,
        source
    ):
        source = self._validate_content_source(
            source
        )
        return SecurityContentSource.is_trusted_source(
            source
        )

    def validate_content(
        self,
        value,
        source,
        field="content",
        boundary=None
    ):
        source = self._validate_content_source(
            source
        )
        normalized_result = self.normalize_input(
            value,
            field
        )
        if normalized_result.is_invalid():
            normalized_result.source = source
            normalized_result.boundary = boundary
            return normalized_result
        normalized_value = normalized_result.value
        instruction_markers = self._find_suspicious_instruction_markers(
            normalized_value
        )
        command_markers = self._find_embedded_command_markers(
            normalized_value
        )
        errors = []
        if (
            instruction_markers
            and self.policy.reject_suspicious_instructions
            and SecurityContentSource.is_untrusted_source(source)
        ):
            error = self._record_failure(
                f"{field} contains suspicious instruction patterns",
                field,
                SecurityContentError
            )
            errors.append(
                str(error)
            )
        if (
            command_markers
            and self.policy.reject_embedded_commands
            and SecurityContentSource.is_untrusted_source(source)
        ):
            error = self._record_failure(
                f"{field} contains embedded command patterns",
                field,
                SecurityContentError
            )
            errors.append(
                str(error)
            )
        result = self._build_result(
            normalized_value,
            errors,
            warnings=[]
        )
        result.boundary = boundary
        result.source = source
        result.instructions_detected = bool(
            instruction_markers
        )
        result.commands_detected = bool(
            command_markers
        )
        return result

    def validate_user_content(
        self,
        value,
        field="user_content"
    ):
        return self.validate_content(
            value,
            SecurityContentSource.USER,
            field,
            TrustBoundary.USER_QUERY
        )

    def validate_retrieved_content(
        self,
        value,
        field="retrieved_content"
    ):
        return self.validate_content(
            value,
            SecurityContentSource.RETRIEVED,
            field,
            TrustBoundary.DOCUMENT
        )

    def validate_external_content(
        self,
        value,
        field="external_content"
    ):
        return self.validate_content(
            value,
            SecurityContentSource.EXTERNAL,
            field,
            TrustBoundary.EXTERNAL_RESPONSE
        )

    def validate_system_content(
        self,
        value,
        field="system_content"
    ):
        return self.validate_content(
            value,
            SecurityContentSource.SYSTEM,
            field,
            TrustBoundary.CONFIGURATION
        )

    def validate_content_package(
        self,
        items,
        field="content_package"
    ):
        if not isinstance(items, (list, tuple)):
            error = self._record_failure(
                f"{field} must be a list or tuple of content items",
                field,
                SecurityContentError
            )
            return self._build_result(
                items,
                [str(error)]
            )
        validated_items = []
        errors = []
        for index, item in enumerate(items):
            item_field = f"{field}[{index}]"
            if not isinstance(item, dict):
                error = self._record_failure(
                    f"{item_field} must be a dictionary",
                    item_field,
                    SecurityContentError
                )
                errors.append(
                    str(error)
                )
                continue
            if "source" not in item:
                error = self._record_failure(
                    f"{item_field} is missing content source metadata",
                    item_field,
                    SecurityContentError
                )
                errors.append(
                    str(error)
                )
                continue
            if "content" not in item:
                error = self._record_failure(
                    f"{item_field} is missing content",
                    item_field,
                    SecurityContentError
                )
                errors.append(
                    str(error)
                )
                continue
            try:
                source = self._validate_content_source(
                    item["source"]
                )
            except Exception as exception:
                errors.append(
                    str(exception)
                )
                continue
            content_result = self.validate_content(
                item["content"],
                source,
                f"{item_field}.content",
                item.get("boundary")
            )
            if content_result.is_invalid():
                errors.extend(
                    content_result.errors
                )
                continue
            validated_items.append(
                {
                    "content": content_result.value,
                    "source": content_result.source,
                    "boundary": content_result.boundary,
                    "trusted": content_result.is_trusted(),
                    "instructions_detected": content_result.instructions_detected,
                    "commands_detected": content_result.commands_detected
                }
            )
        return self._build_result(
            validated_items,
            errors
        )

    def get_content_metadata(
        self,
        result
    ):
        if not isinstance(result, ValidationResult):
            raise ValueError(
                "Security content metadata requires a ValidationResult"
            )
        return {
            "source": result.source,
            "trusted": result.is_trusted(),
            "boundary": result.boundary,
            "instructions_detected": result.instructions_detected,
            "commands_detected": result.commands_detected
        }

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
            "supported_content_sources": list(
                SecurityContentSource.ALL
            ),
            "trusted_content_sources": list(
                SecurityContentSource.TRUSTED
            ),
            "untrusted_content_sources": list(
                SecurityContentSource.UNTRUSTED
            ),
            "supported_trust_boundaries": self.get_trust_boundaries(),
            "trusted_boundaries": self.get_trusted_boundaries()
        }