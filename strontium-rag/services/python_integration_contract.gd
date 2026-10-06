class_name StrontiumPythonIntegrationContract
extends RefCounted


const PROTOCOL_NAME: String = "strontium.rag"
const CONTRACT_VERSION: String = "1.0"

const MESSAGE_TYPE_REQUEST: String = "request"
const MESSAGE_TYPE_RESPONSE: String = "response"


const FIELD_PROTOCOL: String = "protocol"
const FIELD_VERSION: String = "version"
const FIELD_TYPE: String = "type"
const FIELD_REQUEST_ID: String = "request_id"
const FIELD_OPERATION: String = "operation"
const FIELD_PAYLOAD: String = "payload"
const FIELD_SUCCESS: String = "success"
const FIELD_DATA: String = "data"
const FIELD_ERROR: String = "error"
const FIELD_METADATA: String = "metadata"


const ERROR_FIELD_CODE: String = "code"
const ERROR_FIELD_MESSAGE: String = "message"
const ERROR_FIELD_DETAILS: String = "details"


const ERROR_INVALID_REQUEST: String = "INVALID_REQUEST"
const ERROR_INVALID_RESPONSE: String = "INVALID_RESPONSE"
const ERROR_INVALID_OPERATION: String = "INVALID_OPERATION"
const ERROR_INVALID_PAYLOAD: String = "INVALID_PAYLOAD"
const ERROR_PROTOCOL_MISMATCH: String = "PROTOCOL_MISMATCH"
const ERROR_VERSION_MISMATCH: String = "VERSION_MISMATCH"
const ERROR_MALFORMED_JSON: String = "MALFORMED_JSON"


const OP_INITIALIZE: String = "initialize"
const OP_INGEST: String = "ingest"
const OP_LIST_DOCUMENTS: String = "list_documents"
const OP_RETRIEVE: String = "retrieve"
const OP_CONSTRUCT_CONTEXT: String = "construct_context"
const OP_GENERATE: String = "generate"
const OP_CITE: String = "cite"
const OP_CONVERSE: String = "converse"
const OP_EVALUATE: String = "evaluate"
const OP_INSPECT_STATUS: String = "inspect_status"


static func get_supported_operations() -> Array[String]:
	return [
		OP_INITIALIZE,
		OP_INGEST,
		OP_LIST_DOCUMENTS,
		OP_RETRIEVE,
		OP_CONSTRUCT_CONTEXT,
		OP_GENERATE,
		OP_CITE,
		OP_CONVERSE,
		OP_EVALUATE,
		OP_INSPECT_STATUS
	]


static func is_supported_operation(
	operation: String
) -> bool:
	return operation in get_supported_operations()


static func create_request(
	operation: String,
	payload: Dictionary = {},
	request_id: String = "",
	metadata: Dictionary = {}
) -> Dictionary:
	var resolved_request_id: String = request_id

	if resolved_request_id.is_empty():
		resolved_request_id = _generate_request_id()

	return {
		FIELD_PROTOCOL: PROTOCOL_NAME,
		FIELD_VERSION: CONTRACT_VERSION,
		FIELD_TYPE: MESSAGE_TYPE_REQUEST,
		FIELD_REQUEST_ID: resolved_request_id,
		FIELD_OPERATION: operation,
		FIELD_PAYLOAD: payload.duplicate(true),
		FIELD_METADATA: metadata.duplicate(true)
	}


static func create_success_response(
	request: Dictionary,
	data: Dictionary = {},
	metadata: Dictionary = {}
) -> Dictionary:
	return {
		FIELD_PROTOCOL: PROTOCOL_NAME,
		FIELD_VERSION: CONTRACT_VERSION,
		FIELD_TYPE: MESSAGE_TYPE_RESPONSE,
		FIELD_REQUEST_ID: str(
			request.get(
				FIELD_REQUEST_ID,
				""
			)
		),
		FIELD_OPERATION: str(
			request.get(
				FIELD_OPERATION,
				""
			)
		),
		FIELD_SUCCESS: true,
		FIELD_DATA: data.duplicate(true),
		FIELD_ERROR: {},
		FIELD_METADATA: metadata.duplicate(true)
	}


static func create_failure_response(
	request: Dictionary,
	error_code: String,
	error_message: String,
	error_details: Dictionary = {},
	metadata: Dictionary = {}
) -> Dictionary:
	return {
		FIELD_PROTOCOL: PROTOCOL_NAME,
		FIELD_VERSION: CONTRACT_VERSION,
		FIELD_TYPE: MESSAGE_TYPE_RESPONSE,
		FIELD_REQUEST_ID: str(
			request.get(
				FIELD_REQUEST_ID,
				""
			)
		),
		FIELD_OPERATION: str(
			request.get(
				FIELD_OPERATION,
				""
			)
		),
		FIELD_SUCCESS: false,
		FIELD_DATA: {},
		FIELD_ERROR: _create_error(
			error_code,
			error_message,
			error_details
		),
		FIELD_METADATA: metadata.duplicate(true)
	}


static func create_standalone_failure_response(
	request_id: String,
	operation: String,
	error_code: String,
	error_message: String,
	error_details: Dictionary = {},
	metadata: Dictionary = {}
) -> Dictionary:
	return {
		FIELD_PROTOCOL: PROTOCOL_NAME,
		FIELD_VERSION: CONTRACT_VERSION,
		FIELD_TYPE: MESSAGE_TYPE_RESPONSE,
		FIELD_REQUEST_ID: request_id,
		FIELD_OPERATION: operation,
		FIELD_SUCCESS: false,
		FIELD_DATA: {},
		FIELD_ERROR: _create_error(
			error_code,
			error_message,
			error_details
		),
		FIELD_METADATA: metadata.duplicate(true)
	}


static func validate_request(
	request: Dictionary
) -> Dictionary:
	var errors: Array[String] = []

	if not request.has(FIELD_PROTOCOL):
		errors.append(
			"Missing protocol field."
		)
	elif str(
		request.get(
			FIELD_PROTOCOL,
			""
		)
	) != PROTOCOL_NAME:
		errors.append(
			"Unsupported protocol."
		)

	if not request.has(FIELD_VERSION):
		errors.append(
			"Missing version field."
		)
	elif not is_compatible_version(
		str(
			request.get(
				FIELD_VERSION,
				""
			)
		)
	):
		errors.append(
			"Unsupported contract version."
		)

	if str(
		request.get(
			FIELD_TYPE,
			""
		)
	) != MESSAGE_TYPE_REQUEST:
		errors.append(
			"Message type must be request."
		)

	var request_id: String = str(
		request.get(
			FIELD_REQUEST_ID,
			""
		)
	)

	if request_id.is_empty():
		errors.append(
			"Missing request ID."
		)

	var operation: String = str(
		request.get(
			FIELD_OPERATION,
			""
		)
	)

	if operation.is_empty():
		errors.append(
			"Missing operation."
	)
	elif not is_supported_operation(operation):
		errors.append(
			"Unsupported operation: " + operation
		)

	var payload_value: Variant = request.get(
		FIELD_PAYLOAD,
		null
	)

	if payload_value == null:
		errors.append(
			"Missing payload."
	)
	elif not (payload_value is Dictionary):
		errors.append(
			"Payload must be a Dictionary."
		)

	var metadata_value: Variant = request.get(
		FIELD_METADATA,
		{}
	)

	if not (metadata_value is Dictionary):
		errors.append(
			"Metadata must be a Dictionary."
		)

	return _validation_result(errors)


static func validate_response(
	response: Dictionary
) -> Dictionary:
	var errors: Array[String] = []

	if not response.has(FIELD_PROTOCOL):
		errors.append(
			"Missing protocol field."
	)
	elif str(
		response.get(
			FIELD_PROTOCOL,
			""
		)
	) != PROTOCOL_NAME:
		errors.append(
			"Unsupported protocol."
		)

	if not response.has(FIELD_VERSION):
		errors.append(
			"Missing version field."
	)
	elif not is_compatible_version(
		str(
			response.get(
				FIELD_VERSION,
				""
			)
		)
	):
		errors.append(
			"Unsupported contract version."
		)

	if str(
		response.get(
			FIELD_TYPE,
			""
		)
	) != MESSAGE_TYPE_RESPONSE:
		errors.append(
			"Message type must be response."
		)

	var request_id: String = str(
		response.get(
			FIELD_REQUEST_ID,
			""
		)
	)

	if request_id.is_empty():
		errors.append(
			"Missing request ID."
		)

	var operation: String = str(
		response.get(
			FIELD_OPERATION,
			""
		)
	)

	if operation.is_empty():
		errors.append(
			"Missing operation."
	)
	elif not is_supported_operation(operation):
		errors.append(
			"Unsupported operation: " + operation
		)

	if not response.has(FIELD_SUCCESS):
		errors.append(
			"Missing success field."
		)
	else:
		var success_value: Variant = response.get(
			FIELD_SUCCESS
		)

		if not (success_value is bool):
			errors.append(
				"Success field must be a boolean."
			)

	var data_value: Variant = response.get(
		FIELD_DATA,
		{}
	)

	if not (data_value is Dictionary):
		errors.append(
			"Data field must be a Dictionary."
		)

	var error_value: Variant = response.get(
		FIELD_ERROR,
		{}
	)

	if not (error_value is Dictionary):
		errors.append(
			"Error field must be a Dictionary."
		)

	var metadata_value: Variant = response.get(
		FIELD_METADATA,
		{}
	)

	if not (metadata_value is Dictionary):
		errors.append(
			"Metadata must be a Dictionary."
		)

	var success: bool = false

	if response_success_is_boolean(response):
		var response_success_value: Variant = (
			response.get(
				FIELD_SUCCESS,
				false
			)
		)

		success = response_success_value

	if success:
		if error_value is Dictionary:
			var error_dictionary: Dictionary = (
				error_value
			)

			if not error_dictionary.is_empty():
				errors.append(
					"Successful responses must not contain an error."
				)

	return _validation_result(errors)


static func serialize_message(
	message: Dictionary
) -> String:
	return JSON.stringify(
		message
	)


static func deserialize_message(
	json_text: String
) -> Dictionary:
	if json_text.is_empty():
		return {}

	var parsed: Variant = _parse_json_safely(
		json_text
	)

	if parsed == null:
		return {}

	if not (parsed is Dictionary):
		return {}

	return parsed


static func validate_serialized_message(
	json_text: String
) -> Dictionary:
	if json_text.is_empty():
		return _validation_result(
		[
			"Serialized message is empty."
		]
	)

	var parsed: Variant = _parse_json_safely(
		json_text
	)

	if parsed == null:
		return _validation_result(
		[
			"Serialized message contains invalid JSON."
		]
	)

	if not (parsed is Dictionary):
		return _validation_result(
			[
				"Serialized message must decode to a Dictionary."
			]
		)

	var dictionary: Dictionary = parsed

	var message_type: String = str(
		dictionary.get(
			FIELD_TYPE,
			""
		)
	)

	if message_type == MESSAGE_TYPE_REQUEST:
		return validate_request(
			dictionary
		)

	if message_type == MESSAGE_TYPE_RESPONSE:
		return validate_response(
			dictionary
		)

	return _validation_result(
		[
			"Unknown message type."
		]
	)


static func is_compatible_version(
	version: String
) -> bool:
	if version.is_empty():
		return false

	var expected_parts: PackedStringArray = (
		CONTRACT_VERSION.split(".")
	)

	var actual_parts: PackedStringArray = (
		version.split(".")
	)

	if expected_parts.size() < 1:
		return false

	if actual_parts.size() < 1:
		return false

	var expected_major: int = int(
		expected_parts[0]
	)

	var actual_major: int = int(
		actual_parts[0]
	)

	if expected_major != actual_major:
		return false

	return true


static func get_contract_definition() -> Dictionary:
	return {
		"protocol": PROTOCOL_NAME,
		"version": CONTRACT_VERSION,
		"request_type": MESSAGE_TYPE_REQUEST,
		"response_type": MESSAGE_TYPE_RESPONSE,
		"operations": get_supported_operations(),
		"request_fields": [
			FIELD_PROTOCOL,
			FIELD_VERSION,
			FIELD_TYPE,
			FIELD_REQUEST_ID,
			FIELD_OPERATION,
			FIELD_PAYLOAD,
			FIELD_METADATA
		],
		"response_fields": [
			FIELD_PROTOCOL,
			FIELD_VERSION,
			FIELD_TYPE,
			FIELD_REQUEST_ID,
			FIELD_OPERATION,
			FIELD_SUCCESS,
			FIELD_DATA,
			FIELD_ERROR,
			FIELD_METADATA
		],
		"error_fields": [
			ERROR_FIELD_CODE,
			ERROR_FIELD_MESSAGE,
			ERROR_FIELD_DETAILS
		]
	}


static func get_contract_version() -> String:
	return CONTRACT_VERSION


static func get_protocol_name() -> String:
	return PROTOCOL_NAME


static func _create_error(
	error_code: String,
	error_message: String,
	error_details: Dictionary
) -> Dictionary:
	return {
		ERROR_FIELD_CODE: error_code,
		ERROR_FIELD_MESSAGE: error_message,
		ERROR_FIELD_DETAILS: error_details.duplicate(true)
	}


static func _validation_result(
	errors: Array[String]
) -> Dictionary:
	return {
		"valid": errors.is_empty(),
		"errors": errors
	}


static func response_success_is_boolean(
	response: Dictionary
) -> bool:
	if not response.has(
		FIELD_SUCCESS
	):
		return false

	var success_value: Variant = (
		response.get(
			FIELD_SUCCESS,
			false
		)
	)

	return success_value is bool


static func _parse_json_safely(
	json_text: String
) -> Variant:
	var parser: JSON = JSON.new()

	var parse_result: Error = (
		parser.parse(
			json_text
		)
	)

	if parse_result != OK:
		return null

	return parser.data


static func _generate_request_id() -> String:
	var timestamp: int = Time.get_unix_time_from_system()
	var random_value: int = randi()

	return (
		"req-"
		+ str(timestamp)
		+ "-"
		+ str(random_value)
	)
