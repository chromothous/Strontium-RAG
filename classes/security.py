# Strontium RAG Security Validator — cumulative through 0.13.16
from classes.logger import Logger
from classes.error_handler import ErrorHandler
import os
import re
import json
import math
import time
import copy
import uuid
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


class SecuritySecretError(SecurityError):
    def __init__(
        self,
        message,
        field=None
    ):
        super().__init__(
            message,
            category="secret"
        )
        if field is not None:
            if not isinstance(field, str) or not field.strip():
                raise ValueError(
                    "Security secret field must be a non-empty string or None"
                )
        self.field = field


class SecurityIdentityError(SecurityError):
    def __init__(
        self,
        message,
        identity_type=None,
        identifier=None
    ):
        super().__init__(
            message,
            category="identity"
        )
        if identity_type is not None:
            if not isinstance(identity_type, str) or not identity_type.strip():
                raise ValueError(
                    "Security identity type must be a non-empty string or None"
                )
        if identifier is not None:
            if not isinstance(identifier, str) or not identifier.strip():
                raise ValueError(
                    "Security identity identifier must be a non-empty string or None"
                )
        self.identity_type = identity_type
        self.identifier = identifier


class SecuritySerializationError(SecurityError):
    def __init__(
        self,
        message,
        field=None
    ):
        super().__init__(
            message,
            category="serialization"
        )
        if field is not None:
            if not isinstance(field, str) or not field.strip():
                raise ValueError(
                    "Security serialization field must be a non-empty string or None"
                )
        self.field = field


class SecurityIsolationError(SecurityError):
    def __init__(
        self,
        message,
        component=None,
        boundary=None
    ):
        super().__init__(
            message,
            category="isolation"
        )
        if component is not None:
            if not isinstance(component, str) or not component.strip():
                raise ValueError(
                    "Security isolation component must be a non-empty string or None"
                )
        if boundary is not None:
            if not isinstance(boundary, str) or not boundary.strip():
                raise ValueError(
                    "Security isolation boundary must be a non-empty string or None"
                )
        self.component = component
        self.boundary = boundary


class SecurityPipelineError(SecurityError):
    def __init__(
        self,
        message,
        stage=None,
        field=None
    ):
        super().__init__(
            message,
            category="pipeline"
        )
        if stage is not None:
            if not isinstance(stage, str) or not stage.strip():
                raise ValueError(
                    "Security pipeline stage must be a non-empty string or None"
                )
        if field is not None:
            if not isinstance(field, str) or not field.strip():
                raise ValueError(
                    "Security pipeline field must be a non-empty string or None"
                )
        self.stage = stage
        self.field = field


class SecurityResourceError(SecurityError):
    def __init__(
        self,
        message,
        resource_type=None,
        field=None
    ):
        super().__init__(
            message,
            category="resource"
        )
        if resource_type is not None:
            if not isinstance(resource_type, str) or not resource_type.strip():
                raise ValueError(
                    "Security resource type must be a non-empty string or None"
                )
        if field is not None:
            if not isinstance(field, str) or not field.strip():
                raise ValueError(
                    "Security resource field must be a non-empty string or None"
                )
        self.resource_type = resource_type
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
        commands_detected=False,
        sensitive=False
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
        if not isinstance(sensitive, bool):
            raise ValueError(
                "Validation result sensitive flag must be a boolean"
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
        self.sensitive = sensitive

    def is_valid(self):
        return self.valid is True

    def is_invalid(self):
        return self.valid is False

    def is_trusted(self):
        return self.trusted is True

    def is_untrusted(self):
        return self.trusted is False

    def is_sensitive(self):
        return self.sensitive is True

    def to_dict(self):
        return {
            "valid": self.valid,
            "value": "[REDACTED]" if self.sensitive else self.value,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "trusted": self.trusted,
            "boundary": self.boundary,
            "source": self.source,
            "instructions_detected": self.instructions_detected,
            "commands_detected": self.commands_detected,
            "sensitive": self.sensitive
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
    DEFAULT_REDACT_SECRETS = True
    DEFAULT_ALLOW_EMPTY_SECRETS = False
    DEFAULT_MIN_SECRET_LENGTH = 8
    DEFAULT_SENSITIVE_FIELD_NAMES = (
        "api_key",
        "apikey",
        "access_token",
        "auth_token",
        "authorization",
        "password",
        "passwd",
        "secret",
        "token",
        "private_key",
        "client_secret",
        "credential",
        "credentials",
    )
    DEFAULT_MAX_IDENTIFIER_LENGTH = 256
    DEFAULT_REJECT_IDENTITY_WHITESPACE = True
    DEFAULT_IDENTITY_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]*$"
    DEFAULT_ALLOWED_IDENTITY_TYPES = (
        "document",
        "source",
        "chunk",
        "conversation",
        "session",
    )
    DEFAULT_MAX_SERIALIZED_SIZE = 1000000
    DEFAULT_ALLOWED_SERIALIZATION_FORMATS = (
        "json",
    )
    DEFAULT_REJECT_UNEXPECTED_SERIALIZED_FIELDS = True
    DEFAULT_ALLOW_NON_FINITE_NUMBERS = False
    DEFAULT_SERIALIZATION_VERSION = "1"
    DEFAULT_MAX_DOCUMENTS_PER_OPERATION = 100
    DEFAULT_MAX_CHUNKS_PER_OPERATION = 1000
    DEFAULT_MAX_METADATA_ITEMS_PER_OPERATION = 1000
    DEFAULT_MAX_CONVERSATION_MESSAGES = 1000
    DEFAULT_MAX_RETRIEVAL_REQUESTS = 100
    DEFAULT_MAX_PROCESSING_ITEMS = 10000
    DEFAULT_MAX_MEMORY_UNITS = 1000000
    DEFAULT_MAX_EXPANSION_RATIO = 10.0
    DEFAULT_MAX_PROCESSING_TIME_MS = 30000
    DEFAULT_SECURITY_AUDIT_LOGGING = True
    DEFAULT_MAX_SECURITY_EVENTS = 1000
    DEFAULT_REDACT_AUDIT_DATA = True
    DEFAULT_ENFORCE_ISOLATION = True
    DEFAULT_PREVENT_VALIDATION_BYPASS = True
    DEFAULT_PRESERVE_TRUST_STATE = True
    DEFAULT_REQUIRE_BOUNDARY_FOR_ISOLATED_DATA = True
    DEFAULT_MAX_ISOLATION_CONTEXTS = 1000
    DEFAULT_ALLOWED_ISOLATION_COMPONENTS = (
        "ingestion",
        "preprocessing",
        "chunking",
        "embedding",
        "retrieval",
        "context",
        "generation",
        "citation",
        "conversation",
        "evaluation",
        "persistence",
        "api",
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
        redact_secrets=DEFAULT_REDACT_SECRETS,
        allow_empty_secrets=DEFAULT_ALLOW_EMPTY_SECRETS,
        min_secret_length=DEFAULT_MIN_SECRET_LENGTH,
        sensitive_field_names=DEFAULT_SENSITIVE_FIELD_NAMES,
        max_identifier_length=DEFAULT_MAX_IDENTIFIER_LENGTH,
        reject_identity_whitespace=DEFAULT_REJECT_IDENTITY_WHITESPACE,
        identity_pattern=DEFAULT_IDENTITY_PATTERN,
        allowed_identity_types=DEFAULT_ALLOWED_IDENTITY_TYPES,
        max_serialized_size=DEFAULT_MAX_SERIALIZED_SIZE,
        allowed_serialization_formats=DEFAULT_ALLOWED_SERIALIZATION_FORMATS,
        reject_unexpected_serialized_fields=DEFAULT_REJECT_UNEXPECTED_SERIALIZED_FIELDS,
        allow_non_finite_numbers=DEFAULT_ALLOW_NON_FINITE_NUMBERS,
        serialization_version=DEFAULT_SERIALIZATION_VERSION,
        max_documents_per_operation=DEFAULT_MAX_DOCUMENTS_PER_OPERATION,
        max_chunks_per_operation=DEFAULT_MAX_CHUNKS_PER_OPERATION,
        max_metadata_items_per_operation=DEFAULT_MAX_METADATA_ITEMS_PER_OPERATION,
        max_conversation_messages=DEFAULT_MAX_CONVERSATION_MESSAGES,
        max_retrieval_requests=DEFAULT_MAX_RETRIEVAL_REQUESTS,
        max_processing_items=DEFAULT_MAX_PROCESSING_ITEMS,
        max_memory_units=DEFAULT_MAX_MEMORY_UNITS,
        max_expansion_ratio=DEFAULT_MAX_EXPANSION_RATIO,
        max_processing_time_ms=DEFAULT_MAX_PROCESSING_TIME_MS,
        security_audit_logging=DEFAULT_SECURITY_AUDIT_LOGGING,
        max_security_events=DEFAULT_MAX_SECURITY_EVENTS,
        redact_audit_data=DEFAULT_REDACT_AUDIT_DATA,
        enforce_isolation=DEFAULT_ENFORCE_ISOLATION,
        prevent_validation_bypass=DEFAULT_PREVENT_VALIDATION_BYPASS,
        preserve_trust_state=DEFAULT_PRESERVE_TRUST_STATE,
        require_boundary_for_isolated_data=DEFAULT_REQUIRE_BOUNDARY_FOR_ISOLATED_DATA,
        max_isolation_contexts=DEFAULT_MAX_ISOLATION_CONTEXTS,
        allowed_isolation_components=DEFAULT_ALLOWED_ISOLATION_COMPONENTS,
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
        if not isinstance(redact_secrets, bool):
            raise ValueError(
                "Security redact_secrets must be a boolean"
            )
        if not isinstance(allow_empty_secrets, bool):
            raise ValueError(
                "Security allow_empty_secrets must be a boolean"
            )
        if not isinstance(min_secret_length, int) or isinstance(min_secret_length, bool):
            raise ValueError(
                "Security min secret length must be an integer"
            )
        if min_secret_length < 1:
            raise ValueError(
                "Security min secret length must be positive"
            )
        if sensitive_field_names is None:
            sensitive_field_names = self.DEFAULT_SENSITIVE_FIELD_NAMES
        if not isinstance(sensitive_field_names, (list, tuple)):
            raise ValueError(
                "Security sensitive field names must be a list or tuple"
            )
        if not sensitive_field_names:
            raise ValueError(
                "Security sensitive field names cannot be empty"
            )
        normalized_sensitive_fields = []
        for field_name in sensitive_field_names:
            if not isinstance(field_name, str) or not field_name.strip():
                raise ValueError(
                    "Security sensitive field names must contain non-empty strings"
                )
            normalized_sensitive_fields.append(
                field_name.strip().lower()
            )
        self.redact_secrets = redact_secrets
        self.allow_empty_secrets = allow_empty_secrets
        self.min_secret_length = min_secret_length
        self.sensitive_field_names = tuple(
            normalized_sensitive_fields
        )
        if not isinstance(max_identifier_length, int) or isinstance(max_identifier_length, bool):
            raise ValueError(
                "Security max identifier length must be an integer"
            )
        if max_identifier_length < 1:
            raise ValueError(
                "Security max identifier length must be positive"
            )
        if not isinstance(reject_identity_whitespace, bool):
            raise ValueError(
                "Security reject_identity_whitespace must be a boolean"
            )
        if not isinstance(identity_pattern, str) or not identity_pattern.strip():
            raise ValueError(
                "Security identity pattern must be a non-empty string"
            )
        try:
            re.compile(identity_pattern)
        except re.error as exception:
            raise ValueError(
                f"Security identity pattern must be valid: {exception}"
            )
        if not isinstance(allowed_identity_types, (list, tuple)):
            raise ValueError(
                "Security allowed identity types must be a list or tuple"
            )
        if not allowed_identity_types:
            raise ValueError(
                "Security allowed identity types cannot be empty"
            )
        normalized_identity_types = []
        for identity_type in allowed_identity_types:
            if not isinstance(identity_type, str) or not identity_type.strip():
                raise ValueError(
                    "Security identity types must contain non-empty strings"
                )
            normalized_identity_types.append(
                identity_type.strip().lower()
            )
        self.max_identifier_length = max_identifier_length
        self.reject_identity_whitespace = reject_identity_whitespace
        self.identity_pattern = identity_pattern
        self.allowed_identity_types = tuple(
            normalized_identity_types
        )

        if not isinstance(max_serialized_size, int) or isinstance(max_serialized_size, bool):
            raise ValueError(
                "Security max serialized size must be an integer"
            )
        if max_serialized_size < 1:
            raise ValueError(
                "Security max serialized size must be positive"
            )
        if not isinstance(allowed_serialization_formats, (list, tuple)):
            raise ValueError(
                "Security allowed serialization formats must be a list or tuple"
            )
        if not allowed_serialization_formats:
            raise ValueError(
                "Security allowed serialization formats cannot be empty"
            )
        normalized_serialization_formats = []
        for serialization_format in allowed_serialization_formats:
            if not isinstance(serialization_format, str) or not serialization_format.strip():
                raise ValueError(
                    "Security serialization formats must contain non-empty strings"
                )
            normalized_serialization_formats.append(
                serialization_format.strip().lower()
            )
        if not isinstance(reject_unexpected_serialized_fields, bool):
            raise ValueError(
                "Security reject_unexpected_serialized_fields must be a boolean"
            )
        if not isinstance(allow_non_finite_numbers, bool):
            raise ValueError(
                "Security allow_non_finite_numbers must be a boolean"
            )
        if not isinstance(serialization_version, str) or not serialization_version.strip():
            raise ValueError(
                "Security serialization version must be a non-empty string"
            )
        if len(serialization_version) > max_field_length:
            raise ValueError(
                "Security serialization version exceeds the maximum field length"
            )
        self.max_serialized_size = max_serialized_size
        self.allowed_serialization_formats = tuple(
            normalized_serialization_formats
        )
        self.reject_unexpected_serialized_fields = reject_unexpected_serialized_fields
        self.allow_non_finite_numbers = allow_non_finite_numbers
        self.serialization_version = serialization_version.strip()
        self.max_documents_per_operation = self._validate_positive_integer(
            max_documents_per_operation,
            "max documents per operation"
        )
        self.max_chunks_per_operation = self._validate_positive_integer(
            max_chunks_per_operation,
            "max chunks per operation"
        )
        self.max_metadata_items_per_operation = self._validate_positive_integer(
            max_metadata_items_per_operation,
            "max metadata items per operation"
        )
        self.max_conversation_messages = self._validate_positive_integer(
            max_conversation_messages,
            "max conversation messages"
        )
        self.max_retrieval_requests = self._validate_positive_integer(
            max_retrieval_requests,
            "max retrieval requests"
        )
        self.max_processing_items = self._validate_positive_integer(
            max_processing_items,
            "max processing items"
        )
        self.max_memory_units = self._validate_positive_integer(
            max_memory_units,
            "max memory units"
        )
        if not isinstance(max_expansion_ratio, (int, float)) or isinstance(max_expansion_ratio, bool):
            raise ValueError(
                "Security max expansion ratio must be a number"
            )
        if not math.isfinite(max_expansion_ratio) or max_expansion_ratio <= 0:
            raise ValueError(
                "Security max expansion ratio must be finite and positive"
            )
        self.max_expansion_ratio = float(max_expansion_ratio)
        self.max_processing_time_ms = self._validate_positive_integer(
            max_processing_time_ms,
            "max processing time"
        )
        if not isinstance(security_audit_logging, bool):
            raise ValueError(
                "Security audit logging must be a boolean"
            )
        if not isinstance(max_security_events, int) or isinstance(max_security_events, bool):
            raise ValueError(
                "Security max security events must be an integer"
            )
        if max_security_events < 1:
            raise ValueError(
                "Security max security events must be positive"
            )
        if not isinstance(redact_audit_data, bool):
            raise ValueError(
                "Security redact audit data must be a boolean"
            )
        self.security_audit_logging = security_audit_logging
        self.max_security_events = max_security_events
        self.redact_audit_data = redact_audit_data
        if not isinstance(enforce_isolation, bool):
            raise ValueError(
                "Security enforce isolation must be a boolean"
            )
        if not isinstance(prevent_validation_bypass, bool):
            raise ValueError(
                "Security prevent validation bypass must be a boolean"
            )
        if not isinstance(preserve_trust_state, bool):
            raise ValueError(
                "Security preserve trust state must be a boolean"
            )
        if not isinstance(require_boundary_for_isolated_data, bool):
            raise ValueError(
                "Security require boundary for isolated data must be a boolean"
            )
        self.enforce_isolation = enforce_isolation
        self.prevent_validation_bypass = prevent_validation_bypass
        self.preserve_trust_state = preserve_trust_state
        self.require_boundary_for_isolated_data = require_boundary_for_isolated_data
        self.max_isolation_contexts = self._validate_positive_integer(
            max_isolation_contexts,
            "max isolation contexts"
        )
        if not isinstance(allowed_isolation_components, (list, tuple)):
            raise ValueError(
                "Security allowed isolation components must be a list or tuple"
            )
        if not allowed_isolation_components:
            raise ValueError(
                "Security allowed isolation components cannot be empty"
            )
        normalized_isolation_components = []
        for component in allowed_isolation_components:
            if not isinstance(component, str) or not component.strip():
                raise ValueError(
                    "Security isolation components must contain non-empty strings"
                )
            normalized_component = component.strip().lower()
            if normalized_component not in normalized_isolation_components:
                normalized_isolation_components.append(normalized_component)
        self.allowed_isolation_components = tuple(
            normalized_isolation_components
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
        if not isinstance(self.redact_secrets, bool):
            raise ValueError(
                "Security redact_secrets must be a boolean"
            )
        if not isinstance(self.allow_empty_secrets, bool):
            raise ValueError(
                "Security allow_empty_secrets must be a boolean"
            )
        if not isinstance(self.min_secret_length, int) or isinstance(self.min_secret_length, bool):
            raise ValueError(
                "Security min secret length must be an integer"
            )
        if self.min_secret_length < 1:
            raise ValueError(
                "Security min secret length must be positive"
            )
        if not isinstance(self.sensitive_field_names, tuple):
            raise ValueError(
                "Security sensitive field names must be a tuple"
            )
        if not self.sensitive_field_names:
            raise ValueError(
                "Security sensitive field names cannot be empty"
            )
        if not isinstance(self.max_identifier_length, int) or isinstance(self.max_identifier_length, bool):
            raise ValueError(
                "Security max identifier length must be an integer"
            )
        if self.max_identifier_length < 1:
            raise ValueError(
                "Security max identifier length must be positive"
            )
        if not isinstance(self.reject_identity_whitespace, bool):
            raise ValueError(
                "Security reject_identity_whitespace must be a boolean"
            )
        if not isinstance(self.identity_pattern, str) or not self.identity_pattern.strip():
            raise ValueError(
                "Security identity pattern must be a non-empty string"
            )
        try:
            re.compile(self.identity_pattern)
        except re.error as exception:
            raise ValueError(
                f"Security identity pattern must be valid: {exception}"
            )
        if not isinstance(self.allowed_identity_types, tuple):
            raise ValueError(
                "Security allowed identity types must be a tuple"
            )
        if not self.allowed_identity_types:
            raise ValueError(
                "Security allowed identity types cannot be empty"
            )
        if not isinstance(self.max_serialized_size, int) or isinstance(self.max_serialized_size, bool):
            raise ValueError(
                "Security max serialized size must be an integer"
            )
        if self.max_serialized_size < 1:
            raise ValueError(
                "Security max serialized size must be positive"
            )
        if not isinstance(self.allowed_serialization_formats, tuple):
            raise ValueError(
                "Security allowed serialization formats must be a tuple"
            )
        if not self.allowed_serialization_formats:
            raise ValueError(
                "Security allowed serialization formats cannot be empty"
            )
        if not isinstance(self.reject_unexpected_serialized_fields, bool):
            raise ValueError(
                "Security reject_unexpected_serialized_fields must be a boolean"
            )
        if not isinstance(self.allow_non_finite_numbers, bool):
            raise ValueError(
                "Security allow_non_finite_numbers must be a boolean"
            )
        if not isinstance(self.serialization_version, str) or not self.serialization_version.strip():
            raise ValueError(
                "Security serialization version must be a non-empty string"
            )
        if len(self.serialization_version) > self.max_field_length:
            raise ValueError(
                "Security serialization version exceeds the maximum field length"
            )
        self._validate_positive_integer(
            self.max_documents_per_operation,
            "max documents per operation"
        )
        self._validate_positive_integer(
            self.max_chunks_per_operation,
            "max chunks per operation"
        )
        self._validate_positive_integer(
            self.max_metadata_items_per_operation,
            "max metadata items per operation"
        )
        self._validate_positive_integer(
            self.max_conversation_messages,
            "max conversation messages"
        )
        self._validate_positive_integer(
            self.max_retrieval_requests,
            "max retrieval requests"
        )
        self._validate_positive_integer(
            self.max_processing_items,
            "max processing items"
        )
        self._validate_positive_integer(
            self.max_memory_units,
            "max memory units"
        )
        if not isinstance(self.max_expansion_ratio, (int, float)) or isinstance(self.max_expansion_ratio, bool):
            raise ValueError(
                "Security max expansion ratio must be a number"
            )
        if not math.isfinite(self.max_expansion_ratio) or self.max_expansion_ratio <= 0:
            raise ValueError(
                "Security max expansion ratio must be finite and positive"
            )
        self._validate_positive_integer(
            self.max_processing_time_ms,
            "max processing time"
        )
        if not isinstance(self.security_audit_logging, bool):
            raise ValueError(
                "Security audit logging must be a boolean"
            )
        if not isinstance(self.max_security_events, int) or isinstance(self.max_security_events, bool):
            raise ValueError(
                "Security max security events must be an integer"
            )
        if self.max_security_events < 1:
            raise ValueError(
                "Security max security events must be positive"
            )
        if not isinstance(self.redact_audit_data, bool):
            raise ValueError(
                "Security redact audit data must be a boolean"
            )
        if not isinstance(self.enforce_isolation, bool):
            raise ValueError(
                "Security enforce isolation must be a boolean"
            )
        if not isinstance(self.prevent_validation_bypass, bool):
            raise ValueError(
                "Security prevent validation bypass must be a boolean"
            )
        if not isinstance(self.preserve_trust_state, bool):
            raise ValueError(
                "Security preserve trust state must be a boolean"
            )
        if not isinstance(self.require_boundary_for_isolated_data, bool):
            raise ValueError(
                "Security require boundary for isolated data must be a boolean"
            )
        self._validate_positive_integer(
            self.max_isolation_contexts,
            "max isolation contexts"
        )
        if not isinstance(self.allowed_isolation_components, tuple):
            raise ValueError(
                "Security allowed isolation components must be a tuple"
            )
        if not self.allowed_isolation_components:
            raise ValueError(
                "Security allowed isolation components cannot be empty"
            )
        for component in self.allowed_isolation_components:
            if not isinstance(component, str) or not component.strip():
                raise ValueError(
                    "Security allowed isolation components must contain non-empty strings"
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

    @classmethod
    def from_dict(
        cls,
        configuration,
        fallback=None,
        strict=True
    ):
        if not isinstance(configuration, dict):
            raise SecurityPolicyError(
                "Security policy configuration must be a dictionary"
            )
        if fallback is not None and not isinstance(fallback, cls):
            raise SecurityPolicyError(
                "Security policy fallback must be a SecurityPolicy or None"
            )
        if not isinstance(strict, bool):
            raise SecurityPolicyError(
                "Security policy strict configuration mode must be a boolean"
            )
        if fallback is None:
            base_configuration = cls().to_dict()
        else:
            fallback.validate()
            base_configuration = fallback.to_dict()
        supported_fields = set(base_configuration.keys())
        unknown_fields = [
            field
            for field in configuration
            if field not in supported_fields
        ]
        if unknown_fields and strict:
            unknown_fields_text = ", ".join(
                sorted(
                    str(field)
                    for field in unknown_fields
                )
            )
            raise SecurityPolicyError(
                f"Security policy configuration contains unsupported fields: {unknown_fields_text}"
            )
        for field, value in configuration.items():
            if field in supported_fields:
                base_configuration[field] = value
        try:
            policy = cls(**base_configuration)
            policy.validate()
            return policy
        except (ValueError, TypeError, SecurityError) as exception:
            if isinstance(exception, SecurityPolicyError):
                raise
            raise SecurityPolicyError(
                f"Security policy configuration is invalid: {exception}"
            )

    @classmethod
    def secure_defaults(cls):
        policy = cls()
        policy.validate()
        return policy

    def configuration_diff(
        self,
        other
    ):
        if not isinstance(other, SecurityPolicy):
            raise SecurityPolicyError(
                "Security policy comparison requires a SecurityPolicy"
            )
        self.validate()
        other.validate()
        current = self.to_dict()
        comparison = other.to_dict()
        return {
            field: {
                "current": current[field],
                "other": comparison[field]
            }
            for field in current
            if current[field] != comparison[field]
        }

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
            "redact_secrets": self.redact_secrets,
            "allow_empty_secrets": self.allow_empty_secrets,
            "min_secret_length": self.min_secret_length,
            "sensitive_field_names": tuple(
                self.sensitive_field_names
            ),
            "max_identifier_length": self.max_identifier_length,
            "reject_identity_whitespace": self.reject_identity_whitespace,
            "identity_pattern": self.identity_pattern,
            "allowed_identity_types": tuple(
                self.allowed_identity_types
            ),
            "max_serialized_size": self.max_serialized_size,
            "allowed_serialization_formats": tuple(
                self.allowed_serialization_formats
            ),
            "reject_unexpected_serialized_fields": self.reject_unexpected_serialized_fields,
            "allow_non_finite_numbers": self.allow_non_finite_numbers,
            "serialization_version": self.serialization_version,
            "max_documents_per_operation": self.max_documents_per_operation,
            "max_chunks_per_operation": self.max_chunks_per_operation,
            "max_metadata_items_per_operation": self.max_metadata_items_per_operation,
            "max_conversation_messages": self.max_conversation_messages,
            "max_retrieval_requests": self.max_retrieval_requests,
            "max_processing_items": self.max_processing_items,
            "max_memory_units": self.max_memory_units,
            "max_expansion_ratio": self.max_expansion_ratio,
            "max_processing_time_ms": self.max_processing_time_ms,
            "security_audit_logging": self.security_audit_logging,
            "max_security_events": self.max_security_events,
            "redact_audit_data": self.redact_audit_data,
            "enforce_isolation": self.enforce_isolation,
            "prevent_validation_bypass": self.prevent_validation_bypass,
            "preserve_trust_state": self.preserve_trust_state,
            "require_boundary_for_isolated_data": self.require_boundary_for_isolated_data,
            "max_isolation_contexts": self.max_isolation_contexts,
            "allowed_isolation_components": tuple(
                self.allowed_isolation_components
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


class SecurityIsolationContext:
    def __init__(
        self,
        token_id,
        owner_id,
        component,
        boundary,
        source,
        trusted,
        validation_id,
        value_id,
        created_at,
        allowed_targets,
        state_version
    ):
        if not isinstance(token_id, str) or not token_id.strip():
            raise ValueError(
                "Security isolation token id must be a non-empty string"
            )
        if not isinstance(owner_id, int) or isinstance(owner_id, bool):
            raise ValueError(
                "Security isolation owner id must be an integer"
            )
        if not isinstance(component, str) or not component.strip():
            raise ValueError(
                "Security isolation component must be a non-empty string"
            )
        if not TrustBoundary.is_valid(boundary):
            raise ValueError(
                f"Security isolation boundary is not supported: {boundary}"
            )
        if source is not None and not SecurityContentSource.is_valid(source):
            raise ValueError(
                f"Security isolation source is not supported: {source}"
            )
        if not isinstance(trusted, bool):
            raise ValueError(
                "Security isolation trusted flag must be a boolean"
            )
        if not isinstance(validation_id, int) or isinstance(validation_id, bool):
            raise ValueError(
                "Security isolation validation id must be an integer"
            )
        if not isinstance(value_id, int) or isinstance(value_id, bool):
            raise ValueError(
                "Security isolation value id must be an integer"
            )
        if not isinstance(created_at, (int, float)) or isinstance(created_at, bool):
            raise ValueError(
                "Security isolation creation time must be numeric"
            )
        if not isinstance(allowed_targets, (list, tuple, set)):
            raise ValueError(
                "Security isolation allowed targets must be a collection"
            )
        normalized_targets = []
        for target in allowed_targets:
            if not isinstance(target, str) or not target.strip():
                raise ValueError(
                    "Security isolation allowed targets must contain non-empty strings"
                )
            normalized_target = target.strip().lower()
            if normalized_target not in normalized_targets:
                normalized_targets.append(normalized_target)
        if not normalized_targets:
            raise ValueError(
                "Security isolation allowed targets cannot be empty"
            )
        if not isinstance(state_version, int) or isinstance(state_version, bool) or state_version < 0:
            raise ValueError(
                "Security isolation state version must be a non-negative integer"
            )
        self._token_id = token_id.strip()
        self._owner_id = owner_id
        self._component = component.strip().lower()
        self._boundary = boundary
        self._source = source
        self._trusted = trusted
        self._validation_id = validation_id
        self._value_id = value_id
        self._created_at = float(created_at)
        self._allowed_targets = tuple(normalized_targets)
        self._state_version = state_version

    @property
    def token_id(self):
        return self._token_id

    @property
    def component(self):
        return self._component

    @property
    def boundary(self):
        return self._boundary

    @property
    def source(self):
        return self._source

    @property
    def trusted(self):
        return self._trusted

    @property
    def created_at(self):
        return self._created_at

    @property
    def allowed_targets(self):
        return tuple(self._allowed_targets)

    @property
    def state_version(self):
        return self._state_version

    def allows_component(self, component):
        if not isinstance(component, str) or not component.strip():
            return False
        return component.strip().lower() in self._allowed_targets

    def to_dict(self):
        return {
            "token_id": self._token_id,
            "component": self._component,
            "boundary": self._boundary,
            "source": self._source,
            "trusted": self._trusted,
            "created_at": self._created_at,
            "allowed_targets": list(self._allowed_targets),
            "state_version": self._state_version
        }


class SecurityPipelineResult(ValidationResult):
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
        commands_detected=False,
        sensitive=False,
        stages=None,
        isolation_context=None,
        protected_state=None
    ):
        super().__init__(
            valid=valid,
            value=value,
            errors=errors or [],
            warnings=warnings or [],
            trusted=trusted,
            boundary=boundary,
            source=source,
            instructions_detected=instructions_detected,
            commands_detected=commands_detected,
            sensitive=sensitive
        )
        if stages is None:
            stages = {}
        if not isinstance(stages, dict):
            raise ValueError(
                "Security pipeline stages must be a dictionary"
            )
        normalized_stages = {}
        for name, stage in stages.items():
            if not isinstance(name, str) or not name.strip():
                raise ValueError(
                    "Security pipeline stage names must be non-empty strings"
                )
            if not isinstance(stage, dict):
                raise ValueError(
                    "Security pipeline stage data must be dictionaries"
                )
            normalized_stages[name.strip()] = copy.deepcopy(stage)
        if isolation_context is not None and not isinstance(
            isolation_context,
            SecurityIsolationContext
        ):
            raise ValueError(
                "Security pipeline isolation context must be a SecurityIsolationContext or None"
            )
        if protected_state is not None and not isinstance(protected_state, str):
            raise ValueError(
                "Security pipeline protected state must be a string or None"
            )
        self.stages = normalized_stages
        self.isolation_context = isolation_context
        self._protected_state = protected_state

    def get_stage(self, stage):
        if not isinstance(stage, str) or not stage.strip():
            raise ValueError(
                "Security pipeline stage must be a non-empty string"
            )
        return copy.deepcopy(
            self.stages.get(stage.strip())
        )

    def get_protected_state(self):
        return self._protected_state

    def to_dict(self):
        data = super().to_dict()
        data["pipeline"] = {
            "stages": copy.deepcopy(self.stages),
            "has_protected_state": self._protected_state is not None,
            "isolation_active": self.isolation_context is not None
        }
        if self.isolation_context is not None:
            data["pipeline"]["isolation_context"] = self.isolation_context.to_dict()
        return data


class SecurityResourceBudget:
    RESOURCE_TYPES = (
        "documents",
        "chunks",
        "metadata_items",
        "conversation_messages",
        "retrieval_requests",
        "processing_items",
        "memory_units"
    )

    def __init__(
        self,
        validator,
        field="workload"
    ):
        if not isinstance(validator, SecurityValidator):
            raise ValueError(
                "Security resource budget validator must be a SecurityValidator"
            )
        if not isinstance(field, str) or not field.strip():
            raise ValueError(
                "Security resource budget field must be a non-empty string"
            )
        self.validator = validator
        self.field = field.strip()
        self.started_at = time.monotonic()
        self.usage = {
            resource_type: 0
            for resource_type in self.RESOURCE_TYPES
        }

    def consume(
        self,
        resource_type,
        amount=1
    ):
        if resource_type not in self.RESOURCE_TYPES:
            raise ValueError(
                "Unsupported security resource type"
            )
        if not isinstance(amount, int) or isinstance(amount, bool) or amount < 0:
            raise ValueError(
                "Security resource budget amount must be a non-negative integer"
            )
        proposed = self.usage[resource_type] + amount
        result = self.validator._validate_resource_count(
            proposed,
            resource_type,
            f"{self.field}.{resource_type}"
        )
        if result.is_valid():
            self.usage[resource_type] = proposed
            result.value = proposed
        return result

    def check_memory(
        self,
        value
    ):
        return self.validator.validate_memory_growth(
            value,
            f"{self.field}.memory"
        )

    def check_expansion(
        self,
        input_count,
        output_count
    ):
        return self.validator.validate_expansion(
            input_count,
            output_count,
            f"{self.field}.expansion"
        )

    def check_processing_time(self):
        return self.validator.validate_processing_time(
            self.started_at,
            f"{self.field}.processing"
        )

    def get_usage(self):
        return dict(self.usage)


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
        self._identity_registry = {}
        self._security_events = []
        self._security_event_sequence = 0
        self._isolation_contexts = {}
        self._revoked_isolation_contexts = set()
        self._security_state_version = 0

    def _infer_security_event_type(
        self,
        exception_type=SecurityValidationError,
        field=None
    ):
        category = getattr(exception_type, "__mro__", (SecurityValidationError,))[0]
        if category is SecuritySecretError:
            return "secret_exposure_prevented"
        if category is SecurityIdentityError:
            return "identity_violation"
        if category is SecuritySerializationError:
            return "serialization_rejected"
        if category is SecurityResourceError:
            return "resource_abuse_prevented"
        if category is SecurityIsolationError:
            return "isolation_violation"
        if category is SecurityPipelineError:
            return "pipeline_violation"
        if category is SecurityPolicyError:
            return "policy_violation"
        if category is SecuritySchemaError:
            return "schema_violation"
        if category is SecurityContentError:
            return "suspicious_content"
        if isinstance(field, str):
            normalized_field = field.strip().lower()
            filesystem_terms = (
                "path",
                "file",
                "directory",
                "filesystem",
                "temp"
            )
            external_terms = (
                "url",
                "uri",
                "endpoint",
                "host",
                "external",
                "provider"
            )
            if any(term in normalized_field for term in filesystem_terms):
                return "filesystem_resource_blocked"
            if any(term in normalized_field for term in external_terms):
                return "external_resource_blocked"
        return "validation_failure"

    def _audit_safe_value(
        self,
        value
    ):
        if isinstance(value, str):
            return self.redact_text(value) if self.policy.redact_audit_data else value
        if value is None or isinstance(value, (bool, int)):
            return value
        if isinstance(value, float):
            if math.isfinite(value):
                return value
            return "[NON_FINITE]"
        if isinstance(value, dict):
            sanitized = {}
            for key, item in value.items():
                normalized_key = str(key)
                if self._is_sensitive_field(normalized_key):
                    sanitized[normalized_key] = "[REDACTED]"
                else:
                    sanitized[normalized_key] = self._audit_safe_value(item)
            return sanitized
        if isinstance(value, (list, tuple, set)):
            return [
                self._audit_safe_value(item)
                for item in value
            ]
        return f"[UNSAFE:{type(value).__name__}]"

    def _record_security_event(
        self,
        event_type,
        message,
        severity="warning",
        field=None,
        details=None
    ):
        if not isinstance(event_type, str) or not event_type.strip():
            raise ValueError(
                "Security event type must be a non-empty string"
            )
        if not isinstance(message, str) or not message.strip():
            raise ValueError(
                "Security event message must be a non-empty string"
            )
        if not isinstance(severity, str) or not severity.strip():
            raise ValueError(
                "Security event severity must be a non-empty string"
            )
        severity = severity.strip().lower()
        if severity not in ("info", "warning", "error", "critical"):
            raise ValueError(
                "Security event severity must be info, warning, error, or critical"
            )
        if field is not None and (not isinstance(field, str) or not field.strip()):
            raise ValueError(
                "Security event field must be a non-empty string or None"
            )
        if details is not None and not isinstance(details, dict):
            raise ValueError(
                "Security event details must be a dictionary or None"
            )
        sanitized_message = (
            self.redact_text(message)
            if self.policy.redact_audit_data
            else message
        )
        sanitized_field = (
            self.redact_text(field)
            if field is not None and self.policy.redact_audit_data
            else field
        )
        sanitized_details = (
            self._audit_safe_value(details)
            if details is not None
            else {}
        )
        self._security_event_sequence += 1
        event = {
            "event_id": f"security-{self._security_event_sequence:08d}",
            "timestamp": time.time(),
            "event_type": event_type.strip().lower(),
            "severity": severity,
            "message": sanitized_message,
            "field": sanitized_field,
            "details": sanitized_details
        }
        if self.policy.security_audit_logging:
            self._security_events.append(event)
            while len(self._security_events) > self.policy.max_security_events:
                self._security_events.pop(0)
            rendered = (
                f"Security audit [{event['event_type']}] {event['message']}"
            )
            if event["field"] is not None:
                rendered += f" field={event['field']}"
            if severity in ("error", "critical"):
                self.logger.error(rendered)
            else:
                self.logger.info(rendered)
        return copy.deepcopy(event)

    def record_security_event(
        self,
        event_type,
        message,
        severity="warning",
        field=None,
        details=None
    ):
        return self._record_security_event(
            event_type,
            message,
            severity,
            field,
            details
        )

    def get_security_events(
        self,
        event_type=None,
        severity=None,
        limit=None
    ):
        if event_type is not None and (not isinstance(event_type, str) or not event_type.strip()):
            raise ValueError(
                "Security event type filter must be a non-empty string or None"
            )
        if severity is not None:
            if not isinstance(severity, str) or not severity.strip():
                raise ValueError(
                    "Security event severity filter must be a non-empty string or None"
                )
            severity = severity.strip().lower()
            if severity not in ("info", "warning", "error", "critical"):
                raise ValueError(
                    "Security event severity filter must be info, warning, error, or critical"
                )
        if limit is not None:
            if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
                raise ValueError(
                    "Security event limit must be a positive integer or None"
                )
        events = list(self._security_events)
        if event_type is not None:
            normalized_type = event_type.strip().lower()
            events = [
                event for event in events
                if event["event_type"] == normalized_type
            ]
        if severity is not None:
            events = [
                event for event in events
                if event["severity"] == severity
            ]
        if limit is not None:
            events = events[-limit:]
        return copy.deepcopy(events)

    def get_security_event_summary(self):
        counts = {}
        severity_counts = {}
        for event in self._security_events:
            event_type = event["event_type"]
            severity = event["severity"]
            counts[event_type] = counts.get(event_type, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        return {
            "enabled": self.policy.security_audit_logging,
            "event_count": len(self._security_events),
            "max_events": self.policy.max_security_events,
            "by_type": counts,
            "by_severity": severity_counts
        }

    def clear_security_events(self):
        count = len(self._security_events)
        self._security_events.clear()
        return count

    def _record_failure(
        self,
        message,
        field=None,
        exception_type=SecurityValidationError
    ):
        event_type = self._infer_security_event_type(
            exception_type,
            field
        )
        self._record_security_event(
            event_type,
            message,
            severity="error",
            field=field,
            details={
                "security_category": getattr(
                    exception_type,
                    "category",
                    "validation"
                )
            }
        )

        if self.error_handler is not None:
            self.error_handler.handle_expected(
                message,
                category="validation",
                component="security",
                operation="validate",
                details={
                    "field": field,
                    "security_event": event_type
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
            commands_detected=result.commands_detected,
            sensitive=result.sensitive
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
            commands_detected=result.commands_detected,
            sensitive=result.sensitive
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

    def _validate_isolation_component(
        self,
        component
    ):
        if not isinstance(component, str) or not component.strip():
            raise ValueError(
                "Security isolation component must be a non-empty string"
            )
        normalized_component = component.strip().lower()
        if normalized_component not in self.policy.allowed_isolation_components:
            raise SecurityIsolationError(
                f"Security isolation component is not allowed: {normalized_component}",
                normalized_component
            )
        return normalized_component

    def create_isolation_context(
        self,
        result,
        component,
        boundary=None,
        allowed_targets=None
    ):
        component = self._validate_isolation_component(
            component
        )
        if not isinstance(result, ValidationResult):
            raise ValueError(
                "Security isolation context requires a ValidationResult"
            )
        if allowed_targets is None:
            allowed_targets = self.policy.allowed_isolation_components
        if not isinstance(allowed_targets, (list, tuple, set)):
            raise ValueError(
                "Security isolation allowed targets must be a collection"
            )
        normalized_targets = []
        for target in allowed_targets:
            normalized_target = self._validate_isolation_component(
                target
            )
            if normalized_target not in normalized_targets:
                normalized_targets.append(normalized_target)
        if not normalized_targets:
            raise ValueError(
                "Security isolation allowed targets cannot be empty"
            )
        if boundary is None:
            boundary = result.boundary
        if boundary is None and self.policy.require_boundary_for_isolated_data:
            error = self._record_failure(
                "Isolated data requires an explicit trust boundary",
                "boundary",
                SecurityIsolationError
            )
            return self._build_result(
                result.value,
                [str(error)]
            )
        if boundary is None or not TrustBoundary.is_valid(boundary):
            if boundary is None:
                message = "Security isolation boundary cannot be None"
            else:
                message = f"Security isolation boundary is not supported: {boundary}"
            error = self._record_failure(
                message,
                "boundary",
                SecurityIsolationError
            )
            return self._build_result(
                result.value,
                [str(error)]
            )
        if result.boundary is not None and result.boundary != boundary:
            error = self._record_failure(
                "Validation result does not belong to the requested isolation boundary",
                "boundary",
                SecurityIsolationError
            )
            return self._build_result(
                result.value,
                [str(error)]
            )
        if not result.is_valid():
            error = self._record_failure(
                "Invalid validation results cannot enter an isolation boundary",
                "isolation",
                SecurityIsolationError
            )
            return self._build_result(
                result.value,
                [str(error)]
            )
        if len(self._isolation_contexts) >= self.policy.max_isolation_contexts:
            error = self._record_failure(
                "Security isolation context limit has been reached",
                "isolation",
                SecurityIsolationError
            )
            return self._build_result(
                result.value,
                [str(error)]
            )
        token_id = uuid.uuid4().hex
        context = SecurityIsolationContext(
            token_id=token_id,
            owner_id=id(self),
            component=component,
            boundary=boundary,
            source=result.source,
            trusted=result.trusted,
            validation_id=id(result),
            value_id=id(result.value),
            created_at=time.time(),
            allowed_targets=normalized_targets,
            state_version=self._security_state_version
        )
        self._isolation_contexts[token_id] = context
        self._record_security_event(
            "isolation_context_created",
            "Security isolation context created",
            severity="info",
            field=component,
            details={
                "token_id": token_id,
                "boundary": boundary,
                "trusted": result.trusted,
                "source": result.source,
                "allowed_targets": normalized_targets
            }
        )
        return ValidationResult(
            valid=True,
            value=context,
            errors=list(result.errors),
            warnings=list(result.warnings),
            trusted=result.trusted,
            boundary=boundary,
            source=result.source,
            instructions_detected=result.instructions_detected,
            commands_detected=result.commands_detected,
            sensitive=result.sensitive
        )

    def validate_isolation_context(
        self,
        context,
        component=None,
        boundary=None,
        require_trusted=False
    ):
        if not isinstance(context, SecurityIsolationContext):
            raise ValueError(
                "Security isolation validation requires a SecurityIsolationContext"
            )
        if component is not None:
            component = self._validate_isolation_component(
                component
            )
        if boundary is not None and not TrustBoundary.is_valid(boundary):
            raise ValueError(
                f"Security isolation boundary is not supported: {boundary}"
            )
        registered = self._isolation_contexts.get(
            context.token_id
        )
        if registered is None:
            error = self._record_failure(
                "Security isolation context is not registered",
                "isolation",
                SecurityIsolationError
            )
            return self._build_result(
                context,
                [str(error)]
            )
        if context._owner_id != id(self):
            error = self._record_failure(
                "Security isolation context belongs to another security validator",
                "isolation",
                SecurityIsolationError
            )
            return self._build_result(
                context,
                [str(error)]
            )
        if context.token_id in self._revoked_isolation_contexts:
            error = self._record_failure(
                "Security isolation context has been revoked",
                "isolation",
                SecurityIsolationError
            )
            return self._build_result(
                context,
                [str(error)]
            )
        if context.state_version != self._security_state_version:
            error = self._record_failure(
                "Security isolation context is stale",
                "isolation",
                SecurityIsolationError
            )
            return self._build_result(
                context,
                [str(error)]
            )
        if not self.policy.enforce_isolation:
            return ValidationResult(
                valid=True,
                value=context,
                errors=[],
                warnings=["Security isolation enforcement is disabled"],
                trusted=context.trusted,
                boundary=context.boundary,
                source=context.source
            )
        if component is not None and not context.allows_component(component):
            error = self._record_failure(
                f"Security isolation context does not allow target component: {component}",
                component,
                SecurityIsolationError
            )
            return self._build_result(
                context,
                [str(error)]
            )
        if boundary is not None and context.boundary != boundary:
            error = self._record_failure(
                "Security isolation context boundary mismatch",
                "boundary",
                SecurityIsolationError
            )
            return self._build_result(
                context,
                [str(error)]
            )
        if require_trusted and not context.trusted:
            error = self._record_failure(
                "Security isolation context is not trusted",
                "isolation",
                SecurityIsolationError
            )
            return self._build_result(
                context,
                [str(error)]
            )
        return ValidationResult(
            valid=True,
            value=context,
            errors=[],
            warnings=[],
            trusted=context.trusted,
            boundary=context.boundary,
            source=context.source
        )

    def handoff_isolated_value(
        self,
        result,
        context,
        target_component,
        boundary=None
    ):
        target_component = self._validate_isolation_component(
            target_component
        )
        if not isinstance(result, ValidationResult):
            raise ValueError(
                "Security isolation handoff requires a ValidationResult"
            )
        context_result = self.validate_isolation_context(
            context,
            component=target_component,
            boundary=boundary
        )
        if context_result.is_invalid():
            return self._build_result(
                result.value,
                list(context_result.errors)
            )
        if self.policy.prevent_validation_bypass:
            if id(result) != context._validation_id:
                error = self._record_failure(
                    "Security isolation handoff detected a validation bypass",
                    target_component,
                    SecurityIsolationError
                )
                return self._build_result(
                    result.value,
                    [str(error)]
                )
            if id(result.value) != context._value_id:
                error = self._record_failure(
                    "Security isolation handoff detected a value substitution",
                    target_component,
                    SecurityIsolationError
                )
                return self._build_result(
                    result.value,
                    [str(error)]
                )
            if result.is_valid() is not True:
                error = self._record_failure(
                    "Invalid validation result cannot cross an isolation boundary",
                    target_component,
                    SecurityIsolationError
                )
                return self._build_result(
                    result.value,
                    [str(error)]
                )
            if result.trusted != context.trusted:
                error = self._record_failure(
                    "Security isolation handoff detected a trust-state change",
                    target_component,
                    SecurityIsolationError
                )
                return self._build_result(
                    result.value,
                    [str(error)]
                )
            if result.boundary != context.boundary:
                error = self._record_failure(
                    "Security isolation handoff detected a boundary change",
                    target_component,
                    SecurityIsolationError
                )
                return self._build_result(
                    result.value,
                    [str(error)]
                )
            if result.source != context.source:
                error = self._record_failure(
                    "Security isolation handoff detected a source change",
                    target_component,
                    SecurityIsolationError
                )
                return self._build_result(
                    result.value,
                    [str(error)]
                )
        transferred = ValidationResult(
            valid=True,
            value=result.value,
            errors=list(result.errors),
            warnings=list(result.warnings),
            trusted=context.trusted if self.policy.preserve_trust_state else result.trusted,
            boundary=context.boundary,
            source=context.source,
            instructions_detected=result.instructions_detected,
            commands_detected=result.commands_detected,
            sensitive=result.sensitive
        )
        self._record_security_event(
            "isolation_handoff",
            "Security isolation context handed off",
            severity="info",
            field=target_component,
            details={
                "token_id": context.token_id,
                "source_component": context.component,
                "target_component": target_component,
                "boundary": context.boundary,
                "trusted": transferred.trusted
            }
        )
        return transferred

    def revoke_isolation_context(
        self,
        context
    ):
        if not isinstance(context, SecurityIsolationContext):
            raise ValueError(
                "Security isolation revocation requires a SecurityIsolationContext"
            )
        if context.token_id not in self._isolation_contexts:
            return False
        self._revoked_isolation_contexts.add(
            context.token_id
        )
        self._isolation_contexts.pop(
            context.token_id,
            None
        )
        self._record_security_event(
            "isolation_context_revoked",
            "Security isolation context revoked",
            severity="info",
            field=context.component,
            details={
                "token_id": context.token_id,
                "boundary": context.boundary
            }
        )
        return True

    def get_isolation_contexts(self):
        return [
            context.to_dict()
            for context in self._isolation_contexts.values()
        ]

    def validate_isolation_integrity(
        self
    ):
        errors = []
        token_ids = list(self._isolation_contexts.keys())
        if len(token_ids) != len(set(token_ids)):
            errors.append("Security isolation context token ids are not unique")
        if len(token_ids) > self.policy.max_isolation_contexts:
            errors.append("Security isolation context count exceeds configured maximum")
        for token_id, context in self._isolation_contexts.items():
            if token_id != context.token_id:
                errors.append("Security isolation context registry key mismatch")
            if context._owner_id != id(self):
                errors.append("Security isolation context owner mismatch")
            if context.state_version != self._security_state_version:
                errors.append("Security isolation context state version mismatch")
            if not TrustBoundary.is_valid(context.boundary):
                errors.append("Security isolation context boundary is invalid")
            if not context.component or context.component not in self.policy.allowed_isolation_components:
                errors.append("Security isolation context component is not allowed")
            for target in context.allowed_targets:
                if target not in self.policy.allowed_isolation_components:
                    errors.append("Security isolation context contains an invalid target component")
                    break
        if errors:
            for message in errors:
                self._record_security_event(
                    "isolation_integrity_failure",
                    message,
                    severity="critical",
                    field="isolation"
                )
            return self._build_result(
                None,
                errors
            )
        return ValidationResult(
            valid=True,
            value=True,
            errors=[],
            warnings=[],
            trusted=True,
            boundary=TrustBoundary.CONFIGURATION
        )

    def get_isolation_state(self):
        return {
            "enabled": self.policy.enforce_isolation,
            "prevent_validation_bypass": self.policy.prevent_validation_bypass,
            "preserve_trust_state": self.policy.preserve_trust_state,
            "require_boundary_for_isolated_data": self.policy.require_boundary_for_isolated_data,
            "max_contexts": self.policy.max_isolation_contexts,
            "active_context_count": len(self._isolation_contexts),
            "revoked_context_count": len(self._revoked_isolation_contexts),
            "security_state_version": self._security_state_version,
            "allowed_components": list(
                self.policy.allowed_isolation_components
            )
        }

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

    def _is_sensitive_field(
        self,
        field
    ):
        if not isinstance(field, str):
            return False
        normalized = field.strip().lower()
        normalized = normalized.replace(
            "-",
            "_"
        )
        normalized = normalized.replace(
            " ",
            "_"
        )
        return normalized in self.policy.sensitive_field_names

    def redact_secret(
        self,
        value
    ):
        if value is None:
            return None
        if not self.policy.redact_secrets:
            return value
        return "[REDACTED]"

    def redact_text(
        self,
        value,
        secrets=None
    ):
        if not isinstance(value, str):
            raise ValueError(
                "Security redaction text must be a string"
            )
        redacted = value
        if not self.policy.redact_secrets:
            return redacted
        if secrets is not None:
            if not isinstance(secrets, (list, tuple, set)):
                raise ValueError(
                    "Security redaction secrets must be a collection"
                )
            normalized_secrets = []
            for secret in secrets:
                if isinstance(secret, str) and secret:
                    normalized_secrets.append(
                        secret
                    )
            for secret in sorted(
                normalized_secrets,
                key=len,
                reverse=True
            ):
                redacted = redacted.replace(
                    secret,
                    "[REDACTED]"
                )
        patterns = (
            r"(?i)(api[_-]?key\s*[:=]\s*)([^\s,;]+)",
            r"(?i)(access[_-]?token\s*[:=]\s*)([^\s,;]+)",
            r"(?i)(auth(?:orization)?\s*[:=]\s*)([^\s,;]+)",
            r"(?i)(password\s*[:=]\s*)([^\s,;]+)",
            r"(?i)(secret\s*[:=]\s*)([^\s,;]+)",
            r"(?i)(client[_-]?secret\s*[:=]\s*)([^\s,;]+)",
            r"(?i)(private[_-]?key\s*[:=]\s*)([^\s,;]+)",
            r"(?i)(bearer\s+)([^\s,;]+)"
        )
        for pattern in patterns:
            redacted = re.sub(
                pattern,
                r"\1[REDACTED]",
                redacted
            )
        return redacted

    def sanitize_for_logging(
        self,
        value,
        secrets=None
    ):
        if isinstance(value, str):
            return self.redact_text(
                value,
                secrets
            )
        if isinstance(value, dict):
            return self.sanitize_metadata(
                value,
                secrets
            )
        if isinstance(value, list):
            return [
                self.sanitize_for_logging(
                    item,
                    secrets
                )
                for item in value
            ]
        if isinstance(value, tuple):
            return tuple(
                self.sanitize_for_logging(
                    item,
                    secrets
                )
                for item in value
            )
        if isinstance(value, set):
            return {
                self.sanitize_for_logging(
                    item,
                    secrets
                )
                for item in value
            }
        return value

    def sanitize_metadata(
        self,
        metadata,
        secrets=None
    ):
        if not isinstance(metadata, dict):
            raise ValueError(
                "Security metadata sanitization requires a dictionary"
            )
        sanitized = {}
        for key, value in metadata.items():
            if self._is_sensitive_field(
                str(key)
            ):
                sanitized[key] = self.redact_secret(
                    value
                )
                continue
            sanitized[key] = self.sanitize_for_logging(
                value,
                secrets
            )
        return sanitized

    def sanitize_configuration(
        self,
        configuration,
        secrets=None
    ):
        if not isinstance(configuration, dict):
            raise ValueError(
                "Security configuration sanitization requires a dictionary"
            )
        return self.sanitize_metadata(
            configuration,
            secrets
        )

    def validate_secret(
        self,
        value,
        field="secret",
        required=True,
        min_length=None
    ):
        if not isinstance(field, str) or not field.strip():
            raise ValueError(
                "Security secret field must be a non-empty string"
            )
        if min_length is None:
            min_length = self.policy.min_secret_length
        if not isinstance(min_length, int) or isinstance(min_length, bool) or min_length < 1:
            raise ValueError(
                "Security secret minimum length must be a positive integer"
            )
        if not isinstance(value, str):
            error = self._record_failure(
                f"{field} must be a string",
                field,
                SecuritySecretError
            )
            return ValidationResult(
                valid=False,
                value=value,
                errors=[str(error)],
                trusted=False,
                sensitive=True
            )
        if not value and (
            required
            or not self.policy.allow_empty_secrets
        ):
            error = self._record_failure(
                f"{field} cannot be empty",
                field,
                SecuritySecretError
            )
            return ValidationResult(
                valid=False,
                value=value,
                errors=[str(error)],
                trusted=False,
                sensitive=True
            )
        if value and len(value) < min_length:
            error = self._record_failure(
                f"{field} is shorter than the minimum secret length",
                field,
                SecuritySecretError
            )
            return ValidationResult(
                valid=False,
                value=value,
                errors=[str(error)],
                trusted=False,
                sensitive=True
            )
        if value and len(value) > self.policy.max_string_length:
            error = self._record_failure(
                f"{field} exceeds the maximum secret length",
                field,
                SecuritySecretError
            )
            return ValidationResult(
                valid=False,
                value=value,
                errors=[str(error)],
                trusted=False,
                sensitive=True
            )
        if value != value.strip():
            error = self._record_failure(
                f"{field} contains leading or trailing whitespace",
                field,
                SecuritySecretError
            )
            return ValidationResult(
                valid=False,
                value=value,
                errors=[str(error)],
                trusted=False,
                sensitive=True
            )
        return ValidationResult(
            valid=True,
            value=value,
            errors=[],
            warnings=[],
            trusted=False,
            sensitive=True
        )

    def validate_api_key(
        self,
        value,
        field="api_key"
    ):
        return self.validate_secret(
            value,
            field,
            required=True
        )

    def validate_environment_secret(
        self,
        name,
        value=None
    ):
        if not isinstance(name, str) or not name.strip():
            raise ValueError(
                "Security environment secret name must be a non-empty string"
            )
        normalized_name = name.strip()
        if value is None:
            value = os.getenv(
                normalized_name
            )
        return self.validate_secret(
            value,
            f"environment:{normalized_name}",
            required=True
        )

    def require_secret(
        self,
        result,
        field="secret"
    ):
        if not isinstance(result, ValidationResult):
            raise ValueError(
                "Security secret result must be a ValidationResult"
            )
        if not result.is_sensitive():
            raise SecuritySecretError(
                f"Security result for {field} is not marked as sensitive",
                field
            )
        if not result.is_valid():
            raise SecuritySecretError(
                f"Security secret validation failed for {field}",
                field
            )
        return result.value

    def get_secret_status(
        self,
        name,
        value=None
    ):
        if not isinstance(name, str) or not name.strip():
            raise ValueError(
                "Security secret status name must be a non-empty string"
            )
        result = self.validate_environment_secret(
            name,
            value
        )
        return {
            "name": name.strip(),
            "present": result.value is not None and result.value != "",
            "valid": result.is_valid(),
            "sensitive": True
        }

    def _validate_identity_type(
        self,
        identity_type
    ):
        if not isinstance(identity_type, str) or not identity_type.strip():
            raise ValueError(
                "Security identity type must be a non-empty string"
            )
        normalized = identity_type.strip().lower()
        if normalized not in self.policy.allowed_identity_types:
            raise SecurityIdentityError(
                "Security identity type is not allowed",
                normalized,
                None
            )
        return normalized

    def _validate_identifier_format(
        self,
        identifier,
        field
    ):
        if not isinstance(identifier, str):
            error = self._record_failure(
                f"{field} must be a string",
                field,
                SecurityIdentityError
            )
            return None, [str(error)]
        if not identifier.strip():
            error = self._record_failure(
                f"{field} cannot be empty",
                field,
                SecurityIdentityError
            )
            return None, [str(error)]
        if len(identifier) > self.policy.max_identifier_length:
            error = self._record_failure(
                f"{field} exceeds the maximum identifier length",
                field,
                SecurityIdentityError
            )
            return None, [str(error)]
        if (
            self.policy.reject_identity_whitespace
            and identifier != identifier.strip()
        ):
            error = self._record_failure(
                f"{field} contains leading or trailing whitespace",
                field,
                SecurityIdentityError
            )
            return None, [str(error)]
        if any(character.isspace() for character in identifier):
            error = self._record_failure(
                f"{field} contains whitespace",
                field,
                SecurityIdentityError
            )
            return None, [str(error)]
        if re.fullmatch(
            self.policy.identity_pattern,
            identifier
        ) is None:
            error = self._record_failure(
                f"{field} contains invalid identity characters",
                field,
                SecurityIdentityError
            )
            return None, [str(error)]
        return identifier, []

    def validate_identifier(
        self,
        identifier,
        identity_type,
        field="identifier",
        register=False,
        metadata=None
    ):
        normalized_type = self._validate_identity_type(
            identity_type
        )
        normalized_identifier, errors = self._validate_identifier_format(
            identifier,
            field
        )
        if errors:
            return ValidationResult(
                valid=False,
                value=identifier,
                errors=errors,
                trusted=False,
                sensitive=False
            )
        if metadata is not None and not isinstance(metadata, dict):
            error = self._record_failure(
                f"{field} metadata must be a dictionary",
                field,
                SecurityIdentityError
            )
            return ValidationResult(
                valid=False,
                value=identifier,
                errors=[str(error)],
                trusted=False
            )
        if register:
            registration = self.register_identity(
                normalized_type,
                normalized_identifier,
                metadata
            )
            if registration.is_invalid():
                return registration
        return ValidationResult(
            valid=True,
            value=normalized_identifier,
            errors=[],
            warnings=[],
            trusted=False
        )

    def register_identity(
        self,
        identity_type,
        identifier,
        metadata=None
    ):
        normalized_type = self._validate_identity_type(
            identity_type
        )
        normalized_identifier, errors = self._validate_identifier_format(
            identifier,
            "identifier"
        )
        if errors:
            return ValidationResult(
                valid=False,
                value=identifier,
                errors=errors,
                trusted=False
            )
        if metadata is None:
            metadata = {}
        if not isinstance(metadata, dict):
            error = self._record_failure(
                "Identity metadata must be a dictionary",
                "metadata",
                SecurityIdentityError
            )
            return ValidationResult(
                valid=False,
                value=identifier,
                errors=[str(error)],
                trusted=False
            )
        registry_key = (
            normalized_type,
            normalized_identifier
        )
        existing = self._identity_registry.get(
            registry_key
        )
        if existing is not None:
            if existing != metadata:
                error = self._record_failure(
                    f"Identity collision detected for {normalized_type}:{normalized_identifier}",
                    "identifier",
                    SecurityIdentityError
                )
                return ValidationResult(
                    valid=False,
                    value=identifier,
                    errors=[str(error)],
                    trusted=False
                )
            return ValidationResult(
                valid=True,
                value=normalized_identifier,
                errors=[],
                warnings=["identity already registered"],
                trusted=False
            )
        self._identity_registry[registry_key] = dict(
            metadata
        )
        return ValidationResult(
            valid=True,
            value=normalized_identifier,
            errors=[],
            warnings=[],
            trusted=False
        )

    def get_identity_metadata(
        self,
        identity_type,
        identifier
    ):
        normalized_type = self._validate_identity_type(
            identity_type
        )
        normalized_identifier, errors = self._validate_identifier_format(
            identifier,
            "identifier"
        )
        if errors:
            raise SecurityIdentityError(
                errors[0],
                normalized_type,
                identifier
            )
        metadata = self._identity_registry.get(
            (
                normalized_type,
                normalized_identifier
            )
        )
        if metadata is None:
            return None
        return dict(metadata)

    def validate_identity_consistency(
        self,
        metadata,
        identity_type="document",
        field="metadata"
    ):
        normalized_type = self._validate_identity_type(
            identity_type
        )
        if not isinstance(metadata, dict):
            error = self._record_failure(
                f"{field} must be a dictionary",
                field,
                SecurityIdentityError
            )
            return ValidationResult(
                valid=False,
                value=metadata,
                errors=[str(error)],
                trusted=False
            )
        identity_field = f"{normalized_type}_id"
        if identity_field not in metadata:
            error = self._record_failure(
                f"{field} is missing required identity field: {identity_field}",
                field,
                SecurityIdentityError
            )
            return ValidationResult(
                valid=False,
                value=metadata,
                errors=[str(error)],
                trusted=False
            )
        identifier_result = self.validate_identifier(
            metadata[identity_field],
            normalized_type,
            identity_field
        )
        if identifier_result.is_invalid():
            return identifier_result
        source_value = metadata.get(
            "source"
        )
        if normalized_type == "document" and source_value is not None:
            source_result = self.validate_identifier(
                source_value,
                "source",
                "source"
            )
            if source_result.is_invalid():
                return source_result
        if normalized_type == "chunk":
            parent_document_id = metadata.get(
                "document_id"
            )
            if parent_document_id is None:
                error = self._record_failure(
                    f"{field} is missing required parent document_id",
                    field,
                    SecurityIdentityError
                )
                return ValidationResult(
                    valid=False,
                    value=metadata,
                    errors=[str(error)],
                    trusted=False
                )
            document_result = self.validate_identifier(
                parent_document_id,
                "document",
                "document_id"
            )
            if document_result.is_invalid():
                return document_result
            if "chunk_index" in metadata:
                chunk_index = metadata["chunk_index"]
                if not isinstance(chunk_index, int) or isinstance(chunk_index, bool) or chunk_index < 0:
                    error = self._record_failure(
                        f"{field}.chunk_index must be a non-negative integer",
                        field,
                        SecurityIdentityError
                    )
                    return ValidationResult(
                        valid=False,
                        value=metadata,
                        errors=[str(error)],
                        trusted=False
                    )
        identity_key = (
            normalized_type,
            identifier_result.value
        )
        registered = self._identity_registry.get(
            identity_key
        )
        if registered is not None and registered != metadata:
            error = self._record_failure(
                f"{field} identity metadata does not match registered identity",
                field,
                SecurityIdentityError
            )
            return ValidationResult(
                valid=False,
                value=metadata,
                errors=[str(error)],
                trusted=False
            )
        return ValidationResult(
            valid=True,
            value=dict(metadata),
            errors=[],
            warnings=[],
            trusted=False
        )

    def validate_document_identity(
        self,
        document_id,
        source=None,
        metadata=None
    ):
        identity_metadata = {}
        if metadata is not None:
            if not isinstance(metadata, dict):
                error = self._record_failure(
                    "Document identity metadata must be a dictionary",
                    "metadata",
                    SecurityIdentityError
                )
                return ValidationResult(
                    valid=False,
                    value=metadata,
                    errors=[str(error)],
                    trusted=False
                )
            identity_metadata.update(
                metadata
            )
        if source is not None:
            identity_metadata["source"] = source
        identity_metadata["document_id"] = document_id
        result = self.validate_identity_consistency(
            identity_metadata,
            "document",
            "document_identity"
        )
        if result.is_invalid():
            return result
        return result

    def validate_chunk_identity(
        self,
        chunk_id,
        document_id,
        chunk_index,
        metadata=None
    ):
        identity_metadata = {}
        if metadata is not None:
            if not isinstance(metadata, dict):
                error = self._record_failure(
                    "Chunk identity metadata must be a dictionary",
                    "metadata",
                    SecurityIdentityError
                )
                return ValidationResult(
                    valid=False,
                    value=metadata,
                    errors=[str(error)],
                    trusted=False
                )
            identity_metadata.update(
                metadata
            )
        identity_metadata["chunk_id"] = chunk_id
        identity_metadata["document_id"] = document_id
        identity_metadata["chunk_index"] = chunk_index
        return self.validate_identity_consistency(
            identity_metadata,
            "chunk",
            "chunk_identity"
        )

    def _validate_serializable_value(
        self,
        value,
        path="value",
        depth=0
    ):
        if depth > self.policy.max_nesting_depth:
            return [
                f"{path} exceeds the maximum allowed nesting depth"
            ]
        if value is None or isinstance(value, bool) or isinstance(value, int):
            return []
        if isinstance(value, float):
            if not self.policy.allow_non_finite_numbers and not math.isfinite(value):
                return [
                    f"{path} contains a non-finite number"
                ]
            return []
        if isinstance(value, str):
            if len(value) > self.policy.max_field_length:
                return [
                    f"{path} exceeds the maximum allowed field length"
                ]
            return []
        if isinstance(value, (list, tuple)):
            if len(value) > self.policy.max_collection_size:
                return [
                    f"{path} exceeds the maximum allowed collection size"
                ]
            errors = []
            for index, item in enumerate(value):
                errors.extend(
                    self._validate_serializable_value(
                        item,
                        f"{path}[{index}]",
                        depth + 1
                    )
                )
            return errors
        if isinstance(value, dict):
            if len(value) > self.policy.max_collection_size:
                return [
                    f"{path} exceeds the maximum allowed collection size"
                ]
            errors = []
            for key, item in value.items():
                if not isinstance(key, str):
                    errors.append(
                        f"{path} contains a non-string object key"
                    )
                    continue
                if len(key) > self.policy.max_field_length:
                    errors.append(
                        f"{path}.{key} exceeds the maximum allowed field length"
                    )
                    continue
                errors.extend(
                    self._validate_serializable_value(
                        item,
                        f"{path}.{key}",
                        depth + 1
                    )
                )
            return errors
        return [
            f"{path} contains an unsupported serialization type: {type(value).__name__}"
        ]

    def _validate_serialization_version(
        self,
        version,
        field="version"
    ):
        if not isinstance(version, str) or not version.strip():
            error = self._record_failure(
                f"{field} must be a non-empty string",
                field,
                SecuritySerializationError
            )
            return None, [str(error)]
        normalized = version.strip()
        if len(normalized) > self.policy.max_field_length:
            error = self._record_failure(
                f"{field} exceeds the maximum allowed field length",
                field,
                SecuritySerializationError
            )
            return None, [str(error)]
        return normalized, []

    def serialize_safe(
        self,
        value,
        schema=None,
        version=None,
        field="serialized"
    ):
        if not isinstance(field, str) or not field.strip():
            raise ValueError(
                "Security serialization field must be a non-empty string"
            )
        if schema is not None and not isinstance(schema, SecuritySchema):
            raise ValueError(
                "Security serialization schema must be a SecuritySchema or None"
            )
        if "json" not in self.policy.allowed_serialization_formats:
            error = self._record_failure(
                "JSON serialization is not allowed by the security policy",
                field,
                SecuritySerializationError
            )
            return self._build_result(
                None,
                [str(error)]
            )
        if schema is not None:
            schema_result = self.validate_schema(
                value,
                schema,
                field
            )
            if schema_result.is_invalid():
                return schema_result
        structure_errors = self._validate_serializable_value(
            value,
            field
        )
        if structure_errors:
            for message in structure_errors:
                self._record_failure(
                    message,
                    field,
                    SecuritySerializationError
                )
            return self._build_result(
                None,
                structure_errors
            )
        if version is None:
            version = self.policy.serialization_version
        normalized_version, version_errors = self._validate_serialization_version(
            version
        )
        if version_errors:
            return self._build_result(
                None,
                version_errors
            )
        payload = {
            "format": "json",
            "version": normalized_version,
            "data": value
        }
        try:
            serialized = json.dumps(
                payload,
                ensure_ascii=False,
                allow_nan=self.policy.allow_non_finite_numbers,
                sort_keys=True,
                separators=(
                    ",",
                    ":"
                )
            )
            serialized_size = len(
                serialized.encode(
                    self.policy.encoding
                )
            )
        except (TypeError, ValueError, UnicodeError, OverflowError) as exception:
            error = self._record_failure(
                f"{field} could not be safely serialized: {exception}",
                field,
                SecuritySerializationError
            )
            return self._build_result(
                None,
                [str(error)]
            )
        if serialized_size > self.policy.max_serialized_size:
            error = self._record_failure(
                f"{field} exceeds the maximum serialized size",
                field,
                SecuritySerializationError
            )
            return self._build_result(
                None,
                [str(error)]
            )
        return ValidationResult(
            valid=True,
            value=serialized,
            errors=[],
            warnings=[],
            trusted=False
        )

    def _parse_safe_serialized_data(
        self,
        data,
        field="serialized"
    ):
        if isinstance(data, bytes):
            raw_data = data
            try:
                data = data.decode(
                    self.policy.encoding
                )
            except (UnicodeDecodeError, LookupError) as exception:
                error = self._record_failure(
                    f"{field} contains invalid encoded data: {exception}",
                    field,
                    SecuritySerializationError
                )
                return None, [str(error)]
        elif isinstance(data, str):
            try:
                raw_data = data.encode(
                    self.policy.encoding
                )
            except (UnicodeEncodeError, LookupError) as exception:
                error = self._record_failure(
                    f"{field} could not be encoded safely: {exception}",
                    field,
                    SecuritySerializationError
                )
                return None, [str(error)]
        else:
            error = self._record_failure(
                f"{field} must be a string or bytes",
                field,
                SecuritySerializationError
            )
            return None, [str(error)]
        if len(raw_data) > self.policy.max_serialized_size:
            error = self._record_failure(
                f"{field} exceeds the maximum serialized size",
                field,
                SecuritySerializationError
            )
            return None, [str(error)]
        return data, []

    def deserialize_safe(
        self,
        data,
        expected_type=None,
        schema=None,
        expected_version=None,
        field="serialized"
    ):
        if not isinstance(field, str) or not field.strip():
            raise ValueError(
                "Security serialization field must be a non-empty string"
            )
        if expected_type is not None and not isinstance(expected_type, type):
            raise ValueError(
                "Security expected serialization type must be a type or None"
            )
        if schema is not None and not isinstance(schema, SecuritySchema):
            raise ValueError(
                "Security deserialization schema must be a SecuritySchema or None"
            )
        raw_data, parse_errors = self._parse_safe_serialized_data(
            data,
            field
        )
        if parse_errors:
            return self._build_result(
                None,
                parse_errors
            )
        def reject_constant(value):
            raise ValueError(
                f"non-finite JSON constant is not allowed: {value}"
            )
        try:
            if self.policy.allow_non_finite_numbers:
                parsed = json.loads(
                    raw_data
                )
            else:
                parsed = json.loads(
                    raw_data,
                    parse_constant=reject_constant
                )
        except (TypeError, ValueError, json.JSONDecodeError) as exception:
            error = self._record_failure(
                f"{field} contains malformed or unsafe JSON: {exception}",
                field,
                SecuritySerializationError
            )
            return self._build_result(
                None,
                [str(error)]
            )
        if not isinstance(parsed, dict):
            error = self._record_failure(
                f"{field} must contain a serialization envelope",
                field,
                SecuritySerializationError
            )
            return self._build_result(
                None,
                [str(error)]
            )
        expected_envelope_fields = {
            "format",
            "version",
            "data"
        }
        envelope_fields = set(parsed.keys())
        missing_fields = expected_envelope_fields - envelope_fields
        unexpected_fields = envelope_fields - expected_envelope_fields
        errors = []
        for missing in sorted(missing_fields):
            errors.append(
                f"{field} is missing required serialization field: {missing}"
            )
        if self.policy.reject_unexpected_serialized_fields:
            for unexpected in sorted(unexpected_fields):
                errors.append(
                    f"{field} contains unexpected serialization field: {unexpected}"
                )
        if errors:
            for message in errors:
                self._record_failure(
                    message,
                    field,
                    SecuritySerializationError
                )
            return self._build_result(
                None,
                errors
            )
        serialization_format = parsed.get(
            "format"
        )
        if not isinstance(serialization_format, str) or serialization_format.strip().lower() not in self.policy.allowed_serialization_formats:
            error = self._record_failure(
                f"{field} uses a serialization format that is not allowed",
                field,
                SecuritySerializationError
            )
            return self._build_result(
                None,
                [str(error)]
            )
        normalized_version, version_errors = self._validate_serialization_version(
            parsed.get("version"),
            f"{field}.version"
        )
        if version_errors:
            return self._build_result(
                None,
                version_errors
            )
        if expected_version is not None:
            expected_normalized, expected_errors = self._validate_serialization_version(
                expected_version,
                f"{field}.expected_version"
            )
            if expected_errors:
                return self._build_result(
                    None,
                    expected_errors
                )
            if normalized_version != expected_normalized:
                error = self._record_failure(
                    f"{field} version is incompatible with the expected version",
                    field,
                    SecuritySerializationError
                )
                return self._build_result(
                    None,
                    [str(error)]
                )
        value = parsed.get(
            "data"
        )
        structure_errors = self._validate_serializable_value(
            value,
            f"{field}.data"
        )
        if structure_errors:
            for message in structure_errors:
                self._record_failure(
                    message,
                    field,
                    SecuritySerializationError
                )
            return self._build_result(
                None,
                structure_errors
            )
        if expected_type is not None and not isinstance(value, expected_type):
            error = self._record_failure(
                f"{field}.data must be of type {expected_type.__name__}",
                field,
                SecuritySerializationError
            )
            return self._build_result(
                None,
                [str(error)]
            )
        if schema is not None:
            schema_result = self.validate_schema(
                value,
                schema,
                f"{field}.data"
            )
            if schema_result.is_invalid():
                return schema_result
        return ValidationResult(
            valid=True,
            value=value,
            errors=[],
            warnings=[],
            trusted=False
        )

    def serialize_state(
        self,
        value,
        schema=None,
        version=None,
        field="state"
    ):
        return self.serialize_safe(
            value,
            schema,
            version,
            field
        )

    def deserialize_state(
        self,
        data,
        expected_type=None,
        schema=None,
        expected_version=None,
        field="state"
    ):
        return self.deserialize_safe(
            data,
            expected_type,
            schema,
            expected_version,
            field
        )

    def _get_resource_limit(self, resource_type):
        limits = {
            "documents": self.policy.max_documents_per_operation,
            "chunks": self.policy.max_chunks_per_operation,
            "metadata_items": self.policy.max_metadata_items_per_operation,
            "conversation_messages": self.policy.max_conversation_messages,
            "retrieval_requests": self.policy.max_retrieval_requests,
            "processing_items": self.policy.max_processing_items,
            "memory_units": self.policy.max_memory_units
        }
        if resource_type not in limits:
            raise ValueError(
                "Unsupported security resource type"
            )
        return limits[resource_type]

    def _validate_resource_count(
        self,
        count,
        resource_type,
        field=None
    ):
        if field is None:
            field = resource_type
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            error = self._record_failure(
                f"{field} must be a non-negative integer",
                field,
                SecurityResourceError
            )
            return self._build_result(
                None,
                [str(error)]
            )
        limit = self._get_resource_limit(
            resource_type
        )
        if count > limit:
            error = self._record_failure(
                f"{field} exceeds the maximum allowed resource count",
                field,
                SecurityResourceError
            )
            return self._build_result(
                None,
                [str(error)]
            )
        return ValidationResult(
            valid=True,
            value=count,
            errors=[],
            warnings=[],
            trusted=False
        )

    def validate_document_count(
        self,
        count,
        field="documents"
    ):
        return self._validate_resource_count(
            count,
            "documents",
            field
        )

    def validate_chunk_count(
        self,
        count,
        field="chunks"
    ):
        return self._validate_resource_count(
            count,
            "chunks",
            field
        )

    def validate_metadata_count(
        self,
        count,
        field="metadata_items"
    ):
        return self._validate_resource_count(
            count,
            "metadata_items",
            field
        )

    def validate_conversation_message_count(
        self,
        count,
        field="conversation_messages"
    ):
        return self._validate_resource_count(
            count,
            "conversation_messages",
            field
        )

    def validate_retrieval_request_count(
        self,
        count,
        field="retrieval_requests"
    ):
        return self._validate_resource_count(
            count,
            "retrieval_requests",
            field
        )

    def validate_processing_item_count(
        self,
        count,
        field="processing_items"
    ):
        return self._validate_resource_count(
            count,
            "processing_items",
            field
        )

    def _estimate_memory_units(
        self,
        value,
        depth=0,
        seen=None
    ):
        if seen is None:
            seen = set()
        if depth > self.policy.max_nesting_depth:
            return None, [
                "resource input exceeds the maximum allowed nesting depth"
            ]
        if isinstance(value, (str, bytes, bytearray)):
            return len(value), []
        if value is None or isinstance(value, (bool, int, float)):
            return 1, []
        if isinstance(value, dict):
            object_id = id(value)
            if object_id in seen:
                return None, [
                    "resource input contains a recursive reference"
                ]
            seen.add(object_id)
            units = 1
            errors = []
            for key, item in value.items():
                key_units, key_errors = self._estimate_memory_units(
                    str(key),
                    depth + 1,
                    seen
                )
                if key_errors:
                    errors.extend(key_errors)
                else:
                    units += key_units
                item_units, item_errors = self._estimate_memory_units(
                    item,
                    depth + 1,
                    seen
                )
                if item_errors:
                    errors.extend(item_errors)
                else:
                    units += item_units
            seen.remove(object_id)
            return units, errors
        if isinstance(value, (list, tuple)):
            object_id = id(value)
            if object_id in seen:
                return None, [
                    "resource input contains a recursive reference"
                ]
            seen.add(object_id)
            units = 1
            errors = []
            for item in value:
                item_units, item_errors = self._estimate_memory_units(
                    item,
                    depth + 1,
                    seen
                )
                if item_errors:
                    errors.extend(item_errors)
                else:
                    units += item_units
            seen.remove(object_id)
            return units, errors
        return 1, []

    def validate_memory_growth(
        self,
        value,
        field="memory"
    ):
        units, errors = self._estimate_memory_units(
            value
        )
        if errors:
            for message in errors:
                self._record_failure(
                    message,
                    field,
                    SecurityResourceError
                )
            return self._build_result(
                None,
                errors
            )
        if units > self.policy.max_memory_units:
            error = self._record_failure(
                f"{field} exceeds the maximum allowed memory growth",
                field,
                SecurityResourceError
            )
            return self._build_result(
                None,
                [str(error)]
            )
        return ValidationResult(
            valid=True,
            value=units,
            errors=[],
            warnings=[],
            trusted=False
        )

    def validate_expansion(
        self,
        input_count,
        output_count,
        field="expansion"
    ):
        if not isinstance(input_count, int) or isinstance(input_count, bool) or input_count < 0:
            error = self._record_failure(
                f"{field}.input_count must be a non-negative integer",
                field,
                SecurityResourceError
            )
            return self._build_result(
                None,
                [str(error)]
            )
        if not isinstance(output_count, int) or isinstance(output_count, bool) or output_count < 0:
            error = self._record_failure(
                f"{field}.output_count must be a non-negative integer",
                field,
                SecurityResourceError
            )
            return self._build_result(
                None,
                [str(error)]
            )
        if output_count > self.policy.max_processing_items:
            error = self._record_failure(
                f"{field}.output_count exceeds the maximum processing items",
                field,
                SecurityResourceError
            )
            return self._build_result(
                None,
                [str(error)]
            )
        if input_count == 0:
            if output_count > 0:
                error = self._record_failure(
                    f"{field} cannot expand from zero input items",
                    field,
                    SecurityResourceError
                )
                return self._build_result(
                    None,
                    [str(error)]
                )
            ratio = 1.0
        else:
            ratio = output_count / input_count
            if ratio > self.policy.max_expansion_ratio:
                error = self._record_failure(
                    f"{field} exceeds the maximum allowed expansion ratio",
                    field,
                    SecurityResourceError
                )
                return self._build_result(
                    None,
                    [str(error)]
                )
        return ValidationResult(
            valid=True,
            value={
                "input_count": input_count,
                "output_count": output_count,
                "ratio": ratio
            },
            errors=[],
            warnings=[],
            trusted=False
        )

    def validate_processing_time(
        self,
        start_time,
        field="processing"
    ):
        if not isinstance(start_time, (int, float)) or isinstance(start_time, bool):
            error = self._record_failure(
                f"{field}.start_time must be a number",
                field,
                SecurityResourceError
            )
            return self._build_result(
                None,
                [str(error)]
            )
        if not math.isfinite(start_time):
            error = self._record_failure(
                f"{field}.start_time must be finite",
                field,
                SecurityResourceError
            )
            return self._build_result(
                None,
                [str(error)]
            )
        elapsed_ms = (time.monotonic() - start_time) * 1000
        if elapsed_ms < 0:
            error = self._record_failure(
                f"{field}.start_time must not be in the future",
                field,
                SecurityResourceError
            )
            return self._build_result(
                None,
                [str(error)]
            )
        if elapsed_ms > self.policy.max_processing_time_ms:
            error = self._record_failure(
                f"{field} exceeds the maximum allowed processing time",
                field,
                SecurityResourceError
            )
            return self._build_result(
                None,
                [str(error)]
            )
        return ValidationResult(
            valid=True,
            value=elapsed_ms,
            errors=[],
            warnings=[],
            trusted=False
        )

    def validate_workload(
        self,
        documents=0,
        chunks=0,
        metadata_items=0,
        conversation_messages=0,
        retrieval_requests=0,
        processing_items=0,
        memory_value=None,
        start_time=None,
        expansion=None,
        field="workload"
    ):
        if not isinstance(field, str) or not field.strip():
            raise ValueError(
                "Security workload field must be a non-empty string"
            )
        checks = [
            (
                "documents",
                documents
            ),
            (
                "chunks",
                chunks
            ),
            (
                "metadata_items",
                metadata_items
            ),
            (
                "conversation_messages",
                conversation_messages
            ),
            (
                "retrieval_requests",
                retrieval_requests
            ),
            (
                "processing_items",
                processing_items
            )
        ]
        errors = []
        for resource_type, count in checks:
            result = self._validate_resource_count(
                count,
                resource_type,
                f"{field}.{resource_type}"
            )
            if result.is_invalid():
                errors.extend(
                    result.errors
                )
        if memory_value is not None:
            memory_result = self.validate_memory_growth(
                memory_value,
                f"{field}.memory"
            )
            if memory_result.is_invalid():
                errors.extend(
                    memory_result.errors
                )
        if start_time is not None:
            processing_result = self.validate_processing_time(
                start_time,
                f"{field}.processing"
            )
            if processing_result.is_invalid():
                errors.extend(
                    processing_result.errors
                )
        if expansion is not None:
            if not isinstance(expansion, (list, tuple)) or len(expansion) != 2:
                raise ValueError(
                    "Security workload expansion must contain input and output counts"
                )
            expansion_result = self.validate_expansion(
                expansion[0],
                expansion[1],
                f"{field}.expansion"
            )
            if expansion_result.is_invalid():
                errors.extend(
                    expansion_result.errors
                )
        if errors:
            return self._build_result(
                None,
                errors
            )
        return ValidationResult(
            valid=True,
            value={
                "documents": documents,
                "chunks": chunks,
                "metadata_items": metadata_items,
                "conversation_messages": conversation_messages,
                "retrieval_requests": retrieval_requests,
                "processing_items": processing_items
            },
            errors=[],
            warnings=[],
            trusted=False
        )

    def create_resource_budget(
        self,
        field="workload"
    ):
        return SecurityResourceBudget(
            self,
            field
        )

    def _validate_pipeline_source(self, source):
        if not isinstance(source, str) or not source.strip():
            raise ValueError(
                "Security pipeline source must be a non-empty string"
            )
        if not SecurityContentSource.is_valid(source):
            raise ValueError(
                f"Security pipeline source is not supported: {source}"
            )
        return source.strip().lower()

    def _validate_pipeline_component(self, component):
        return self._validate_isolation_component(
            component
        )

    def _pipeline_failure(
        self,
        stages,
        value,
        errors,
        boundary,
        source,
        field,
        trusted=False,
        instructions_detected=False,
        commands_detected=False,
        sensitive=False,
        isolation_context=None,
        protected_state=None
    ):
        normalized_errors = [
            str(error)
            for error in errors
        ]
        return SecurityPipelineResult(
            valid=False,
            value=value,
            errors=normalized_errors,
            warnings=[],
            trusted=trusted,
            boundary=boundary,
            source=source,
            instructions_detected=instructions_detected,
            commands_detected=commands_detected,
            sensitive=sensitive,
            stages=stages,
            isolation_context=isolation_context,
            protected_state=protected_state
        )

    def _normalize_pipeline_value(
        self,
        value,
        field,
        depth=0
    ):
        if depth > self.policy.max_nesting_depth:
            error = self._record_failure(
                f"{field} exceeds the maximum allowed nesting depth during normalization",
                field,
                SecurityPipelineError
            )
            return self._build_result(
                value,
                [str(error)]
            )
        if isinstance(value, str):
            return self.validate_normalization_order(
                value,
                field
            )
        if isinstance(value, dict):
            if len(value) > self.policy.max_collection_size:
                error = self._record_failure(
                    f"{field} contains too many fields during normalization",
                    field,
                    SecurityPipelineError
                )
                return self._build_result(
                    value,
                    [str(error)]
                )
            normalized = {}
            errors = []
            for key, item in value.items():
                if not isinstance(key, str) or not key.strip():
                    error = self._record_failure(
                        f"{field} contains an invalid field name during normalization",
                        field,
                        SecurityPipelineError
                    )
                    errors.append(
                        str(error)
                    )
                    continue
                child_result = self._normalize_pipeline_value(
                    item,
                    f"{field}.{key}",
                    depth + 1
                )
                if child_result.is_invalid():
                    errors.extend(
                        child_result.errors
                    )
                else:
                    normalized[key] = child_result.value
            return self._build_result(
                normalized if not errors else value,
                errors
            )
        if isinstance(value, list):
            if len(value) > self.policy.max_collection_size:
                error = self._record_failure(
                    f"{field} contains too many items during normalization",
                    field,
                    SecurityPipelineError
                )
                return self._build_result(
                    value,
                    [str(error)]
                )
            normalized = []
            errors = []
            for index, item in enumerate(value):
                child_result = self._normalize_pipeline_value(
                    item,
                    f"{field}[{index}]",
                    depth + 1
                )
                if child_result.is_invalid():
                    errors.extend(
                        child_result.errors
                    )
                else:
                    normalized.append(
                        child_result.value
                    )
            return self._build_result(
                normalized if not errors else value,
                errors
            )
        if isinstance(value, tuple):
            normalized = []
            errors = []
            if len(value) > self.policy.max_collection_size:
                error = self._record_failure(
                    f"{field} contains too many items during normalization",
                    field,
                    SecurityPipelineError
                )
                return self._build_result(
                    value,
                    [str(error)]
                )
            for index, item in enumerate(value):
                child_result = self._normalize_pipeline_value(
                    item,
                    f"{field}[{index}]",
                    depth + 1
                )
                if child_result.is_invalid():
                    errors.extend(
                        child_result.errors
                    )
                else:
                    normalized.append(
                        child_result.value
                    )
            return self._build_result(
                tuple(normalized) if not errors else value,
                errors
            )
        return self._build_result(
            value
        )

    def _validate_pipeline_security_stage(
        self,
        value,
        boundary,
        source,
        field,
        schema=None
    ):
        if schema is not None and not isinstance(schema, SecuritySchema):
            raise ValueError(
                "Security pipeline schema must be a SecuritySchema or None"
            )
        if boundary in (
            TrustBoundary.USER_QUERY,
            TrustBoundary.DOCUMENT,
            TrustBoundary.EXTERNAL_RESPONSE
        ):
            content_result = self.validate_content(
                value,
                source,
                field,
                boundary
            )
            if content_result.is_invalid():
                return content_result
            value = content_result.value
            if schema is not None:
                schema_result = self.validate_schema(
                    value,
                    schema,
                    field
                )
                if schema_result.is_invalid():
                    return schema_result
            return content_result
        if boundary == TrustBoundary.FILE_PATH:
            return self.validate_safe_file_path(
                value,
                field
            )
        if boundary == TrustBoundary.URL:
            return self.validate_url(
                value,
                field
            )
        if isinstance(value, dict):
            mapping_result = self.validate_mapping(
                value,
                field
            )
            if mapping_result.is_invalid():
                return mapping_result
            if schema is not None:
                return self.validate_schema(
                    value,
                    schema,
                    field
                )
            return mapping_result
        if isinstance(value, (list, tuple, set)):
            collection_result = self.validate_collection(
                value,
                field
            )
            if collection_result.is_invalid():
                return collection_result
            if schema is not None:
                return self.validate_schema(
                    value,
                    schema,
                    field
                )
            return collection_result
        if schema is not None:
            return self.validate_schema(
                value,
                schema,
                field
            )
        return self._build_result(
            value
        )

    def _validate_pipeline_resource_stage(
        self,
        value,
        boundary,
        field
    ):
        checks = []
        if isinstance(value, str):
            if boundary == TrustBoundary.USER_QUERY:
                checks.append(
                    self.validate_query_size(
                        value,
                        field
                    )
                )
            elif boundary == TrustBoundary.DOCUMENT:
                checks.append(
                    self.validate_document_size(
                        len(value.encode(self.policy.encoding)),
                        field
                    )
                )
            elif boundary == TrustBoundary.CONVERSATION_STATE:
                checks.append(
                    self.validate_conversation_history_size(
                        len(value.encode(self.policy.encoding)),
                        field
                    )
                )
            else:
                checks.append(
                    self.validate_size_limit(
                        len(value.encode(self.policy.encoding)),
                        self.policy.max_string_length,
                        field,
                        "pipeline string size"
                    )
                )
        elif isinstance(value, bytes):
            checks.append(
                self.validate_document_size(
                    len(value),
                    field
                )
            )
        else:
            checks.append(
                self.validate_complexity(
                    value,
                    field
                )
            )
            if isinstance(value, dict):
                if boundary == TrustBoundary.METADATA:
                    checks.append(
                        self.validate_metadata_count(
                            len(value),
                            field
                        )
                    )
                elif boundary == TrustBoundary.CONVERSATION_STATE:
                    checks.append(
                        self.validate_conversation_message_count(
                            len(value),
                            field
                        )
                    )
            elif isinstance(value, (list, tuple, set)):
                if boundary == TrustBoundary.DOCUMENT:
                    checks.append(
                        self.validate_document_count(
                            len(value),
                            field
                        )
                    )
                elif boundary == TrustBoundary.CONVERSATION_STATE:
                    checks.append(
                        self.validate_conversation_message_count(
                            len(value),
                            field
                        )
                    )
                elif boundary == TrustBoundary.DOCUMENT:
                    checks.append(
                        self.validate_processing_item_count(
                            len(value),
                            field
                        )
                    )
        checks.append(
            self.validate_memory_growth(
                value,
                f"{field}.memory"
            )
        )
        for check in checks:
            if check.is_invalid():
                return self._build_result(
                    value,
                    check.errors
                )
        return self._build_result(
            value
        )

    def validate_security_pipeline(
        self,
        value,
        boundary,
        source,
        field="input",
        schema=None,
        expected_type=None,
        version=None,
        component="api",
        allowed_targets=None
    ):
        boundary = self._validate_trust_boundary(
            boundary
        )
        source = self._validate_pipeline_source(
            source
        )
        component = self._validate_pipeline_component(
            component
        )
        if not isinstance(field, str) or not field.strip():
            raise ValueError(
                "Security pipeline field must be a non-empty string"
            )
        if expected_type is not None and not isinstance(expected_type, type):
            raise ValueError(
                "Security pipeline expected type must be a type or None"
            )
        if schema is not None and not isinstance(schema, SecuritySchema):
            raise ValueError(
                "Security pipeline schema must be a SecuritySchema or None"
            )
        stages = {}
        boundary_result = self.validate_trust_boundary(
            value,
            boundary,
            field
        )
        boundary_result.source = source
        stages["boundary_validation"] = {
            "valid": boundary_result.is_valid(),
            "boundary": boundary,
            "source": source
        }
        if boundary_result.is_invalid():
            self._record_security_event(
                "pipeline_rejected",
                "Security pipeline rejected input at the boundary validation stage",
                severity="error",
                field=field,
                details={
                    "stage": "boundary_validation",
                    "boundary": boundary,
                    "source": source
                }
            )
            return self._pipeline_failure(
                stages,
                value,
                boundary_result.errors,
                boundary,
                source,
                field
            )
        normalized_result = self._normalize_pipeline_value(
            boundary_result.value,
            field
        )
        stages["normalization"] = {
            "valid": normalized_result.is_valid()
        }
        if normalized_result.is_invalid():
            self._record_security_event(
                "pipeline_rejected",
                "Security pipeline rejected input during normalization",
                severity="error",
                field=field,
                details={
                    "stage": "normalization",
                    "boundary": boundary
                }
            )
            return self._pipeline_failure(
                stages,
                normalized_result.value,
                normalized_result.errors,
                boundary,
                source,
                field
            )
        security_result = self._validate_pipeline_security_stage(
            normalized_result.value,
            boundary,
            source,
            field,
            schema
        )
        security_result.source = source
        security_result.boundary = boundary
        if SecurityContentSource.is_trusted_source(source):
            security_result = self.mark_trusted(
                security_result
            )
            security_result.source = source
            security_result.boundary = boundary
        stages["security_checks"] = {
            "valid": security_result.is_valid(),
            "instructions_detected": security_result.instructions_detected,
            "commands_detected": security_result.commands_detected
        }
        if security_result.is_invalid():
            self._record_security_event(
                "pipeline_rejected",
                "Security pipeline rejected input during security checks",
                severity="error",
                field=field,
                details={
                    "stage": "security_checks",
                    "boundary": boundary,
                    "source": source
                }
            )
            return self._pipeline_failure(
                stages,
                security_result.value,
                security_result.errors,
                boundary,
                source,
                field,
                instructions_detected=security_result.instructions_detected,
                commands_detected=security_result.commands_detected,
                sensitive=security_result.sensitive
            )
        resource_result = self._validate_pipeline_resource_stage(
            security_result.value,
            boundary,
            field
        )
        stages["resource_limits"] = {
            "valid": resource_result.is_valid()
        }
        if resource_result.is_invalid():
            self._record_security_event(
                "pipeline_rejected",
                "Security pipeline rejected input at the resource limit stage",
                severity="error",
                field=field,
                details={
                    "stage": "resource_limits",
                    "boundary": boundary
                }
            )
            return self._pipeline_failure(
                stages,
                security_result.value,
                resource_result.errors,
                boundary,
                source,
                field,
                instructions_detected=security_result.instructions_detected,
                commands_detected=security_result.commands_detected,
                sensitive=security_result.sensitive
            )
        isolation_result = self.create_isolation_context(
            security_result,
            component,
            boundary,
            allowed_targets
        )
        stages["safe_processing"] = {
            "valid": isolation_result.is_valid(),
            "component": component,
            "isolation_created": isolation_result.is_valid()
        }
        if isolation_result.is_invalid():
            self._record_security_event(
                "pipeline_rejected",
                "Security pipeline rejected input at the isolation stage",
                severity="error",
                field=field,
                details={
                    "stage": "safe_processing",
                    "component": component,
                    "boundary": boundary
                }
            )
            return self._pipeline_failure(
                stages,
                security_result.value,
                isolation_result.errors,
                boundary,
                source,
                field,
                instructions_detected=security_result.instructions_detected,
                commands_detected=security_result.commands_detected,
                sensitive=security_result.sensitive
            )
        isolation_context = isolation_result.value
        validated_isolation = self.validate_isolation_context(
            isolation_context,
            component,
            boundary,
            require_trusted=False
        )
        if validated_isolation.is_invalid():
            self.revoke_isolation_context(
                isolation_context
            )
            stages["safe_processing"]["valid"] = False
            return self._pipeline_failure(
                stages,
                security_result.value,
                validated_isolation.errors,
                boundary,
                source,
                field,
                instructions_detected=security_result.instructions_detected,
                commands_detected=security_result.commands_detected,
                sensitive=security_result.sensitive
            )
        protected_result = self.serialize_safe(
            security_result.value,
            schema=schema,
            version=version,
            field=f"{field}.protected_state"
        )
        stages["protected_state"] = {
            "valid": protected_result.is_valid(),
            "serialization_format": "json" if protected_result.is_valid() else None
        }
        if protected_result.is_invalid():
            self.revoke_isolation_context(
                isolation_context
            )
            return self._pipeline_failure(
                stages,
                security_result.value,
                protected_result.errors,
                boundary,
                source,
                field,
                instructions_detected=security_result.instructions_detected,
                commands_detected=security_result.commands_detected,
                sensitive=security_result.sensitive,
                isolation_context=isolation_context
            )
        output_result = self.deserialize_safe(
            protected_result.value,
            expected_type=expected_type,
            schema=schema,
            expected_version=version,
            field=f"{field}.safe_output"
        )
        stages["safe_output"] = {
            "valid": output_result.is_valid(),
            "type": type(output_result.value).__name__ if output_result.is_valid() else None
        }
        if output_result.is_invalid():
            self.revoke_isolation_context(
                isolation_context
            )
            return self._pipeline_failure(
                stages,
                security_result.value,
                output_result.errors,
                boundary,
                source,
                field,
                instructions_detected=security_result.instructions_detected,
                commands_detected=security_result.commands_detected,
                sensitive=security_result.sensitive,
                isolation_context=isolation_context,
                protected_state=protected_result.value
            )
        trusted = bool(
            security_result.trusted
        )
        if SecurityContentSource.is_trusted_source(source):
            trusted = True
        final_result = SecurityPipelineResult(
            valid=True,
            value=output_result.value,
            errors=[],
            warnings=list(output_result.warnings),
            trusted=trusted,
            boundary=boundary,
            source=source,
            instructions_detected=security_result.instructions_detected,
            commands_detected=security_result.commands_detected,
            sensitive=security_result.sensitive,
            stages=stages,
            isolation_context=isolation_context,
            protected_state=protected_result.value
        )
        self._record_security_event(
            "pipeline_completed",
            "Security validation pipeline completed successfully",
            severity="info",
            field=field,
            details={
                "boundary": boundary,
                "source": source,
                "component": component,
                "trusted": trusted,
                "stages": list(stages.keys()),
                "isolation_token": isolation_context.token_id
            }
        )
        return final_result

    def get_security_pipeline_state(
        self,
        result
    ):
        if not isinstance(result, SecurityPipelineResult):
            raise ValueError(
                "Security pipeline state requires a SecurityPipelineResult"
            )
        context = result.isolation_context
        return {
            "valid": result.is_valid(),
            "trusted": result.is_trusted(),
            "boundary": result.boundary,
            "source": result.source,
            "stages": copy.deepcopy(result.stages),
            "isolation_active": context is not None,
            "isolation_token": context.token_id if context is not None else None,
            "has_protected_state": result.get_protected_state() is not None
        }

    def get_protected_pipeline_state(
        self,
        result,
        component=None,
        boundary=None
    ):
        if not isinstance(result, SecurityPipelineResult):
            raise ValueError(
                "Protected pipeline state requires a SecurityPipelineResult"
            )
        if result.is_invalid():
            error = self._record_failure(
                "Invalid security pipeline results cannot release protected state",
                "pipeline",
                SecurityPipelineError
            )
            return self._build_result(
                None,
                [str(error)]
            )
        context = result.isolation_context
        if context is None:
            error = self._record_failure(
                "Security pipeline result has no active isolation context",
                "pipeline",
                SecurityPipelineError
            )
            return self._build_result(
                None,
                [str(error)]
            )
        validation = self.validate_isolation_context(
            context,
            component,
            boundary,
            require_trusted=False
        )
        if validation.is_invalid():
            return self._build_result(
                None,
                validation.errors
            )
        return ValidationResult(
            valid=True,
            value=result.get_protected_state(),
            errors=[],
            warnings=[],
            trusted=result.trusted,
            boundary=result.boundary,
            source=result.source,
            instructions_detected=result.instructions_detected,
            commands_detected=result.commands_detected,
            sensitive=result.sensitive
        )

    def release_security_pipeline(
        self,
        result
    ):
        if not isinstance(result, SecurityPipelineResult):
            raise ValueError(
                "Security pipeline release requires a SecurityPipelineResult"
            )
        context = result.isolation_context
        if context is None:
            return False
        released = self.revoke_isolation_context(
            context
        )
        if released:
            result.isolation_context = None
            self._record_security_event(
                "pipeline_released",
                "Security validation pipeline isolation context released",
                severity="info",
                field="pipeline",
                details={
                    "boundary": result.boundary,
                    "source": result.source
                }
            )
        return released

    def get_identity_registry(self):
        return {
            f"{identity_type}:{identifier}": dict(metadata)
            for (
                identity_type,
                identifier
            ), metadata in self._identity_registry.items()
        }

    def validate_policy_configuration(
        self,
        configuration,
        fallback=None,
        strict=True
    ):
        if fallback is None:
            fallback = self.policy
        try:
            candidate = SecurityPolicy.from_dict(
                configuration,
                fallback=fallback,
                strict=strict
            )
        except SecurityPolicyError as exception:
            self._record_security_event(
                "policy_violation",
                str(exception),
                severity="error",
                field="policy_configuration",
                details={
                    "operation": "validate_policy_configuration"
                }
            )
            return self._build_result(
                None,
                [str(exception)]
            )
        return ValidationResult(
            valid=True,
            value=candidate,
            errors=[],
            warnings=[],
            trusted=False
        )

    def apply_policy_configuration(
        self,
        configuration,
        fallback_to_current=True,
        strict=True
    ):
        if not isinstance(fallback_to_current, bool):
            raise ValueError(
                "Security policy fallback mode must be a boolean"
            )
        fallback = self.policy if fallback_to_current else SecurityPolicy.secure_defaults()
        result = self.validate_policy_configuration(
            configuration,
            fallback=fallback,
            strict=strict
        )
        if result.is_invalid():
            return result
        previous_policy = self.policy
        self.policy = result.value
        self._security_state_version += 1
        self._isolation_contexts.clear()
        self._revoked_isolation_contexts.clear()
        differences = previous_policy.configuration_diff(
            self.policy
        )
        self._record_security_event(
            "policy_configuration_applied",
            "Security policy configuration applied successfully",
            severity="info",
            field="policy_configuration",
            details={
                "changed_fields": sorted(differences.keys()),
                "fallback_to_current": fallback_to_current,
                "strict": strict
            }
        )
        return ValidationResult(
            valid=True,
            value=self.policy,
            errors=[],
            warnings=[],
            trusted=False
        )

    def set_policy(
        self,
        policy
    ):
        if not isinstance(policy, SecurityPolicy):
            raise ValueError(
                "Security validator policy must be a SecurityPolicy"
            )
        policy.validate()
        previous_policy = self.policy
        differences = previous_policy.configuration_diff(
            policy
        )
        self.policy = policy
        self._security_state_version += 1
        self._isolation_contexts.clear()
        self._revoked_isolation_contexts.clear()
        self._record_security_event(
            "policy_replaced",
            "Security policy replaced successfully",
            severity="info",
            field="policy",
            details={
                "changed_fields": sorted(differences.keys())
            }
        )
        return self.policy

    def reset_policy(self):
        default_policy = SecurityPolicy.secure_defaults()
        previous_policy = self.policy
        differences = previous_policy.configuration_diff(
            default_policy
        )
        self.policy = default_policy
        self._security_state_version += 1
        self._isolation_contexts.clear()
        self._revoked_isolation_contexts.clear()
        self._record_security_event(
            "policy_reset",
            "Security policy reset to secure defaults",
            severity="info",
            field="policy",
            details={
                "changed_fields": sorted(differences.keys())
            }
        )
        return self.policy

    def get_policy(self):
        self.policy.validate()
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
            "secret_protection": {
                "redact_secrets": self.policy.redact_secrets,
                "allow_empty_secrets": self.policy.allow_empty_secrets,
                "min_secret_length": self.policy.min_secret_length,
                "sensitive_field_names": list(
                    self.policy.sensitive_field_names
                )
            },
            "identity_protection": {
                "max_identifier_length": self.policy.max_identifier_length,
                "reject_identity_whitespace": self.policy.reject_identity_whitespace,
                "identity_pattern": self.policy.identity_pattern,
                "allowed_identity_types": list(
                    self.policy.allowed_identity_types
                ),
                "registered_identity_count": len(
                    self._identity_registry
                )
            },
            "serialization_protection": {
                "max_serialized_size": self.policy.max_serialized_size,
                "allowed_serialization_formats": list(
                    self.policy.allowed_serialization_formats
                ),
                "reject_unexpected_serialized_fields": self.policy.reject_unexpected_serialized_fields,
                "allow_non_finite_numbers": self.policy.allow_non_finite_numbers,
                "serialization_version": self.policy.serialization_version
            },
            "audit_logging": {
                "enabled": self.policy.security_audit_logging,
                "max_events": self.policy.max_security_events,
                "redact_audit_data": self.policy.redact_audit_data,
                "event_count": len(self._security_events),
                "event_types": sorted({
                    event["event_type"]
                    for event in self._security_events
                })
            },
            "policy_configuration": {
                "secure_defaults_available": True,
                "configuration_valid": True,
                "supported_fields": sorted(
                    self.policy.to_dict().keys()
                )
            },
            "isolation_protection": self.get_isolation_state(),
            "resource_protection": {
                "max_documents_per_operation": self.policy.max_documents_per_operation,
                "max_chunks_per_operation": self.policy.max_chunks_per_operation,
                "max_metadata_items_per_operation": self.policy.max_metadata_items_per_operation,
                "max_conversation_messages": self.policy.max_conversation_messages,
                "max_retrieval_requests": self.policy.max_retrieval_requests,
                "max_processing_items": self.policy.max_processing_items,
                "max_memory_units": self.policy.max_memory_units,
                "max_expansion_ratio": self.policy.max_expansion_ratio,
                "max_processing_time_ms": self.policy.max_processing_time_ms
            },
            "pipeline_protection": {
                "enabled": True,
                "stages": [
                    "boundary_validation",
                    "normalization",
                    "security_checks",
                    "resource_limits",
                    "safe_processing",
                    "protected_state",
                    "safe_output"
                ],
                "active_isolation_contexts": len(self._isolation_contexts)
            },
            "supported_trust_boundaries": self.get_trust_boundaries(),
            "trusted_boundaries": self.get_trusted_boundaries()
        }