extends Node


signal startup_completed
signal shutdown_started


const RUN_INTERNAL_TESTS: bool = true


const CONTRACT = preload(
	"res://services/python_integration_contract.gd"
)


@onready var app_state: Node = ApplicationState
@onready var application_window: Window = get_window()
@onready var application_service: Node = $ApplicationService
@onready var navigation_service: Node = $NavigationService
@onready var screen_registry: ScreenRegistry = $ScreenRegistry
@onready var debug_service: DebugService = $DebugService
@onready var ui_root: Control = $UIRoot
@onready var content_root: Control = $UIRoot/ContentRoot
@onready var modal_root: Control = $UIRoot/ModalRoot
@onready var header: StrontiumHeader = (
	$UIRoot/HeaderRoot as StrontiumHeader
)
@onready var navigation_ui: StrontiumNavigation = (
	$UIRoot/NavigationRoot as StrontiumNavigation
)
@onready var footer: StrontiumFooter = (
	$UIRoot/StatusRoot as StrontiumFooter
)


var theme_service: StrontiumThemeService


func _ready() -> void:
	application_window.close_requested.connect(
		_on_close_requested
	)

	modal_root.mouse_filter = Control.MOUSE_FILTER_IGNORE

	_initialize_theme_service()

	navigation_service.navigation_changed.connect(
		_on_navigation_changed
	)

	header.set_status(
		"INITIALIZING",
		StrontiumTokens.STATE_INFO
	)

	footer.set_status(
		"STARTING",
		StrontiumStatusIndicator.StatusType.ACTIVE
	)

	start_application()


func _initialize_theme_service() -> void:
	theme_service = StrontiumThemeService.new()
	theme_service.name = "ThemeService"

	add_child(theme_service)

	theme_service.configure(
		ui_root
	)

	theme_service.initialize()

	debug_service.write(
		"Global Strontium theme applied."
	)


func start_application() -> void:
	app_state.mark_starting()

	header.set_status(
		"STARTING",
		StrontiumTokens.STATE_INFO
	)

	footer.set_status(
		"STARTING",
		StrontiumStatusIndicator.StatusType.ACTIVE
	)

	print(
		"Strontium RAG application starting."
	)

	debug_service.initialize()

	debug_service.write(
		"Application startup sequence beginning."
	)

	application_service.initialize()

	debug_service.write(
		"ApplicationService initialized."
	)

	screen_registry.initialize()

	debug_service.write(
		"ScreenRegistry initialized."
	)

	navigation_service.configure(
		content_root,
		screen_registry
	)

	debug_service.write(
		"NavigationService configured."
	)

	navigation_ui.configure(
		navigation_service,
		screen_registry
	)

	debug_service.write(
		"Navigation UI configured."
	)

	navigation_service.navigate_to(
		"Home"
	)

	debug_service.write(
		"Initial navigation completed."
	)

	footer.set_destination(
		navigation_service.get_current_destination()
	)

	app_state.mark_ready()

	header.set_status(
		"SYSTEM READY",
		StrontiumTokens.STATE_SUCCESS
	)

	footer.set_status(
		"READY",
		StrontiumStatusIndicator.StatusType.SUCCESS
	)

	startup_completed.emit()

	print(
		"Strontium RAG application initialized."
	)

	print(
		"Application state: "
		+ app_state.get_status_name()
	)

	print(
		"Application service initialized: "
		+ str(
			application_service.is_initialized()
		)
	)

	print(
		"Registered destinations: "
		+ str(
			screen_registry.get_destinations()
		)
	)

	print(
		"Current destination: "
		+ navigation_service.get_current_destination()
	)

	if RUN_INTERNAL_TESTS:
		call_deferred(
			"_run_internal_tests"
		)


func shutdown_application() -> void:
	if app_state.is_shutting_down():
		return

	app_state.begin_shutdown()

	header.set_status(
		"SHUTTING DOWN",
		StrontiumTokens.STATE_WARNING
	)

	footer.set_status(
		"SHUTTING DOWN",
		StrontiumStatusIndicator.StatusType.WARNING
	)

	shutdown_started.emit()

	debug_service.write(
		"Application shutdown sequence beginning."
	)

	application_service.shutdown()

	debug_service.write(
		"ApplicationService shutdown completed."
	)

	debug_service.shutdown()

	print(
		"Strontium RAG application shutting down."
	)

	print(
		"Application service shutting down: "
		+ str(
			application_service.is_shutting_down()
		)
	)


func _on_navigation_changed(
	_previous_destination: String,
	current_destination: String
) -> void:
	footer.set_destination(
		current_destination
	)


func _on_close_requested() -> void:
	shutdown_application()
	get_tree().quit()


func _exit_tree() -> void:
	if not app_state.is_shutting_down():
		shutdown_application()


# ============================================================
# INTERNAL TEST SUITE
# 0.15.16 — Python Integration Contract
# ============================================================


var internal_tests: int = 0
var internal_success: int = 0
var internal_failure: int = 0


func _run_internal_tests() -> void:
	print("")
	print("========================================")
	print("STRONTIUM INTERNAL TEST SUITE")
	print("0.15.16 — Python Integration Contract")
	print("========================================")

	_test_contract_definition()
	_test_supported_operations()
	_test_request_creation()
	_test_request_validation()
	_test_success_response()
	_test_failure_response()
	_test_standalone_failure_response()
	_test_response_validation()
	_test_serialization()
	_test_serialized_validation()
	_test_version_compatibility()
	_test_contract_accessors()
	_test_request_id_generation()

	print("")
	print("========================================")
	print("INTERNAL TEST SUITE COMPLETE")
	print("Tests: ", internal_tests)
	print("Success: ", internal_success)
	print("Failure: ", internal_failure)

	if internal_failure == 0:
		print(
			"Version 0.15.16 Python Integration Contract is online."
		)
	else:
		print(
			"Version 0.15.16 failed."
		)

	print("========================================")
	print("")


func _record_internal_test(
	test_name: String,
	passed: bool
) -> void:
	internal_tests += 1

	if passed:
		internal_success += 1

		print(
			"[PASS] ",
			test_name
		)
	else:
		internal_failure += 1

		print(
			"[FAIL] ",
			test_name
		)

		push_error(
			"0.15.16 test failed: "
			+ test_name
		)


func _check_internal(
	condition: bool,
	detail: String
) -> bool:
	if condition:
		return true

	print(
		"    [FAIL CHECK] ",
		detail
	)

	return false


func _test_contract_definition() -> void:
	var definition: Dictionary = (
		CONTRACT.get_contract_definition()
	)

	var passed: bool = true

	if not _check_internal(
		definition.has("protocol"),
		"Contract definition should expose protocol."
	):
		passed = false

	if not _check_internal(
		definition["protocol"] == "strontium.rag",
		"Contract protocol should be strontium.rag."
	):
		passed = false

	if not _check_internal(
		definition.has("version"),
		"Contract definition should expose version."
	):
		passed = false

	if not _check_internal(
		definition["version"] == "1.0",
		"Contract version should be 1.0."
	):
		passed = false

	if not _check_internal(
		definition["request_type"] == "request",
		"Request type should be request."
	):
		passed = false

	if not _check_internal(
		definition["response_type"] == "response",
		"Response type should be response."
	):
		passed = false

	if not _check_internal(
		definition["operations"].size() == 10,
		"Contract should expose ten operations."
	):
		passed = false

	if not _check_internal(
		definition["request_fields"].size() == 7,
		"Contract should expose seven request fields."
	):
		passed = false

	if not _check_internal(
		definition["response_fields"].size() == 9,
		"Contract should expose nine response fields."
	):
		passed = false

	if not _check_internal(
		definition["error_fields"].size() == 3,
		"Contract should expose three error fields."
	):
		passed = false

	_record_internal_test(
		"Contract definition",
		passed
	)


func _test_supported_operations() -> void:
	var operations: Array[String] = (
		CONTRACT.get_supported_operations()
	)

	var expected_operations: Array[String] = [
		"initialize",
		"ingest",
		"list_documents",
		"retrieve",
		"construct_context",
		"generate",
		"cite",
		"converse",
		"evaluate",
		"inspect_status"
	]

	var passed: bool = true

	if not _check_internal(
		operations.size() == expected_operations.size(),
		"Supported operation count should match the contract."
	):
		passed = false

	if not _check_internal(
		operations == expected_operations,
		"Supported operations should match the defined operation order."
	):
		passed = false

	for operation in expected_operations:
		var operation_supported: bool = (
			CONTRACT.is_supported_operation(
				operation
			)
		)

		if not _check_internal(
			operation_supported,
			"Operation should be supported: "
			+ operation
		):
			passed = false

	var unsupported_operation: bool = (
		CONTRACT.is_supported_operation(
			"unsupported_operation"
		)
	)

	if not _check_internal(
		not unsupported_operation,
		"Unknown operations should be rejected."
	):
		passed = false

	_record_internal_test(
		"Supported operation identifiers",
		passed
	)


func _test_request_creation() -> void:
	var request: Dictionary = (
		CONTRACT.create_request(
			"retrieve",
			{
				"query": "What is retrieval augmented generation?"
			}
		)
	)

	var passed: bool = true

	if not _check_internal(
		request.has("protocol"),
		"Request should contain protocol."
	):
		passed = false

	if not _check_internal(
		request["protocol"] == "strontium.rag",
		"Request protocol should match the contract."
	):
		passed = false

	if not _check_internal(
		request["version"] == "1.0",
		"Request version should match the contract."
	):
		passed = false

	if not _check_internal(
		request["type"] == "request",
		"Request type should be request."
	):
		passed = false

	if not _check_internal(
		not str(
			request["request_id"]
		).is_empty(),
		"Request should receive a request ID."
	):
		passed = false

	if not _check_internal(
		request["operation"] == "retrieve",
		"Request operation should be retrieve."
	):
		passed = false

	if not _check_internal(
		request["payload"]["query"]
		== "What is retrieval augmented generation?",
		"Request payload should preserve the query."
	):
		passed = false

	if not _check_internal(
		request["metadata"] is Dictionary,
		"Request metadata should be a Dictionary."
	):
		passed = false

	var validation: Dictionary = (
		CONTRACT.validate_request(
			request
		)
	)

	if not _check_internal(
		validation["valid"] == true,
		"Newly created requests should validate successfully."
	):
		passed = false

	_record_internal_test(
		"Request creation",
		passed
	)


func _test_request_validation() -> void:
	var valid_request: Dictionary = (
		CONTRACT.create_request(
			"retrieve",
			{
				"query": "test"
			}
		)
	)

	var passed: bool = true

	var valid_result: Dictionary = (
		CONTRACT.validate_request(
			valid_request
		)
	)

	if not _check_internal(
		valid_result["valid"] == true,
		"Valid request should pass validation."
	):
		passed = false

	var missing_protocol: Dictionary = (
		valid_request.duplicate(true)
	)

	missing_protocol.erase(
		"protocol"
	)

	var missing_protocol_result: Dictionary = (
		CONTRACT.validate_request(
			missing_protocol
		)
	)

	if not _check_internal(
		missing_protocol_result["valid"] == false,
		"Request without protocol should fail validation."
	):
		passed = false

	var invalid_operation: Dictionary = (
		valid_request.duplicate(true)
	)

	invalid_operation["operation"] = "invalid"

	var invalid_operation_result: Dictionary = (
		CONTRACT.validate_request(
			invalid_operation
		)
	)

	if not _check_internal(
		invalid_operation_result["valid"] == false,
		"Unsupported operation should fail validation."
	):
		passed = false

	var invalid_payload: Dictionary = (
		valid_request.duplicate(true)
	)

	invalid_payload["payload"] = "invalid"

	var invalid_payload_result: Dictionary = (
		CONTRACT.validate_request(
			invalid_payload
		)
	)

	if not _check_internal(
		invalid_payload_result["valid"] == false,
		"Non-Dictionary payload should fail validation."
	):
		passed = false

	var missing_request_id: Dictionary = (
		valid_request.duplicate(true)
	)

	missing_request_id.erase(
		"request_id"
	)

	var missing_request_id_result: Dictionary = (
		CONTRACT.validate_request(
			missing_request_id
		)
	)

	if not _check_internal(
		missing_request_id_result["valid"] == false,
		"Request without request ID should fail validation."
	):
		passed = false

	_record_internal_test(
		"Request validation",
		passed
	)


func _test_success_response() -> void:
	var request: Dictionary = (
		CONTRACT.create_request(
			"retrieve",
			{
				"query": "test"
			},
			"req-test-success"
		)
	)

	var response: Dictionary = (
		CONTRACT.create_success_response(
			request,
			{
				"results": [
					{
						"document_id": "doc-1"
					}
				]
			}
		)
	)

	var passed: bool = true

	if not _check_internal(
		response["type"] == "response",
		"Response type should be response."
	):
		passed = false

	if not _check_internal(
		response["request_id"] == "req-test-success",
		"Response should preserve request ID."
	):
		passed = false

	if not _check_internal(
		response["operation"] == "retrieve",
		"Response should preserve operation."
	):
		passed = false

	if not _check_internal(
		response["success"] == true,
		"Successful response should mark success true."
	):
		passed = false

	if not _check_internal(
		response["data"]["results"].size() == 1,
		"Successful response should preserve result data."
	):
		passed = false

	if not _check_internal(
		response["error"].is_empty(),
		"Successful response should contain no error."
	):
		passed = false

	var validation: Dictionary = (
		CONTRACT.validate_response(
			response
		)
	)

	if not _check_internal(
		validation["valid"] == true,
		"Successful response should validate."
	):
		passed = false

	_record_internal_test(
		"Successful response",
		passed
	)


func _test_failure_response() -> void:
	var request: Dictionary = (
		CONTRACT.create_request(
			"generate",
			{
				"prompt": "test"
			},
			"req-test-failure"
		)
	)

	var response: Dictionary = (
		CONTRACT.create_failure_response(
			request,
			"GENERATION_FAILED",
			"Generation failed.",
			{
				"reason": "provider unavailable"
			}
		)
	)

	var passed: bool = true

	if not _check_internal(
		response["success"] == false,
		"Failure response should mark success false."
	):
		passed = false

	if not _check_internal(
		response["data"].is_empty(),
		"Failure response should contain empty data."
	):
		passed = false

	if not _check_internal(
		response["error"]["code"]
		== "GENERATION_FAILED",
		"Failure response should preserve error code."
	):
		passed = false

	if not _check_internal(
		response["error"]["message"]
		== "Generation failed.",
		"Failure response should preserve error message."
	):
		passed = false

	if not _check_internal(
		response["error"]["details"]["reason"]
		== "provider unavailable",
		"Failure response should preserve error details."
	):
		passed = false

	var validation: Dictionary = (
		CONTRACT.validate_response(
			response
		)
	)

	if not _check_internal(
		validation["valid"] == true,
		"Structured failure response should validate."
	):
		passed = false

	_record_internal_test(
		"Failure response",
		passed
	)


func _test_standalone_failure_response() -> void:
	var response: Dictionary = (
		CONTRACT.create_standalone_failure_response(
			"req-standalone",
			"ingest",
			"INGESTION_FAILED",
			"Ingestion failed.",
			{
				"reason": "file unavailable"
			}
		)
	)

	var passed: bool = true

	if not _check_internal(
		response["protocol"] == "strontium.rag",
		"Standalone response should use the contract protocol."
	):
		passed = false

	if not _check_internal(
		response["version"] == "1.0",
		"Standalone response should use the contract version."
	):
		passed = false

	if not _check_internal(
		response["type"] == "response",
		"Standalone response should be a response."
	):
		passed = false

	if not _check_internal(
		response["request_id"] == "req-standalone",
		"Standalone response should preserve request ID."
	):
		passed = false

	if not _check_internal(
		response["operation"] == "ingest",
		"Standalone response should preserve operation."
	):
		passed = false

	if not _check_internal(
		response["success"] == false,
		"Standalone response should indicate failure."
	):
		passed = false

	if not _check_internal(
		response["error"]["code"]
		== "INGESTION_FAILED",
		"Standalone response should preserve error code."
	):
		passed = false

	if not _check_internal(
		response["error"]["details"]["reason"]
		== "file unavailable",
		"Standalone response should preserve error details."
	):
		passed = false

	var validation: Dictionary = (
		CONTRACT.validate_response(
			response
		)
	)

	if not _check_internal(
		validation["valid"] == true,
		"Standalone failure response should validate."
	):
		passed = false

	_record_internal_test(
		"Standalone failure response",
		passed
	)


func _test_response_validation() -> void:
	var request: Dictionary = (
		CONTRACT.create_request(
			"retrieve",
			{},
			"req-response-validation"
		)
	)

	var valid_response: Dictionary = (
		CONTRACT.create_success_response(
			request,
			{
				"value": "ok"
			}
		)
	)

	var passed: bool = true

	var valid_result: Dictionary = (
		CONTRACT.validate_response(
			valid_response
		)
	)

	if not _check_internal(
		valid_result["valid"] == true,
		"Valid response should pass validation."
	):
		passed = false

	var invalid_success: Dictionary = (
		valid_response.duplicate(true)
	)

	invalid_success["success"] = "true"

	var invalid_success_result: Dictionary = (
		CONTRACT.validate_response(
			invalid_success
		)
	)

	if not _check_internal(
		invalid_success_result["valid"] == false,
		"Non-Boolean success field should fail validation."
	):
		passed = false

	var invalid_data: Dictionary = (
		valid_response.duplicate(true)
	)

	invalid_data["data"] = "invalid"

	var invalid_data_result: Dictionary = (
		CONTRACT.validate_response(
			invalid_data
		)
	)

	if not _check_internal(
		invalid_data_result["valid"] == false,
		"Non-Dictionary data should fail validation."
	):
		passed = false

	var invalid_error: Dictionary = (
		valid_response.duplicate(true)
	)

	invalid_error["error"] = "invalid"

	var invalid_error_result: Dictionary = (
		CONTRACT.validate_response(
			invalid_error
		)
	)

	if not _check_internal(
		invalid_error_result["valid"] == false,
		"Non-Dictionary error should fail validation."
	):
		passed = false

	var success_with_error: Dictionary = (
		valid_response.duplicate(true)
	)

	success_with_error["error"] = {
		"code": "INVALID_STATE",
		"message": "Should not exist.",
		"details": {}
	}

	var success_with_error_result: Dictionary = (
		CONTRACT.validate_response(
			success_with_error
		)
	)

	if not _check_internal(
		success_with_error_result["valid"] == false,
		"Successful response containing an error should fail validation."
	):
		passed = false

	_record_internal_test(
		"Response validation",
		passed
	)


func _test_serialization() -> void:
	var request: Dictionary = (
		CONTRACT.create_request(
			"ingest",
			{
				"path": "example.txt"
			},
			"req-serialization"
		)
	)

	var serialized: String = (
		CONTRACT.serialize_message(
			request
		)
	)

	var restored: Dictionary = (
		CONTRACT.deserialize_message(
			serialized
		)
	)

	var passed: bool = true

	if not _check_internal(
		not serialized.is_empty(),
		"Serialized request should not be empty."
	):
		passed = false

	if not _check_internal(
		restored == request,
		"Deserialized request should equal the original request."
	):
		passed = false

	var empty_result: Dictionary = (
		CONTRACT.deserialize_message(
			""
		)
	)

	if not _check_internal(
		empty_result == {},
		"Empty JSON input should return an empty Dictionary."
	):
		passed = false

	var malformed_result: Dictionary = (
		CONTRACT.deserialize_message(
			"not valid json"
		)
	)

	if not _check_internal(
		malformed_result == {},
		"Malformed JSON should return an empty Dictionary."
	):
		passed = false

	var array_result: Dictionary = (
		CONTRACT.deserialize_message(
			"[1,2,3]"
		)
	)

	if not _check_internal(
		array_result == {},
		"JSON arrays should not deserialize as contract messages."
	):
		passed = false

	_record_internal_test(
		"Serialization and deserialization",
		passed
	)


func _test_serialized_validation() -> void:
	var request: Dictionary = (
		CONTRACT.create_request(
			"initialize",
			{},
			"req-serialized-validation"
		)
	)

	var serialized_request: String = (
		CONTRACT.serialize_message(
			request
		)
	)

	var request_validation: Dictionary = (
		CONTRACT.validate_serialized_message(
			serialized_request
		)
	)

	var response: Dictionary = (
		CONTRACT.create_success_response(
			request,
			{
				"ready": true
			}
		)
	)

	var serialized_response: String = (
		CONTRACT.serialize_message(
			response
		)
	)

	var response_validation: Dictionary = (
		CONTRACT.validate_serialized_message(
			serialized_response
		)
	)

	var invalid_json_result: Dictionary = (
		CONTRACT.validate_serialized_message(
			"{invalid"
		)
	)

	var array_json_result: Dictionary = (
		CONTRACT.validate_serialized_message(
			"[1,2,3]"
		)
	)

	var passed: bool = true

	if not _check_internal(
		request_validation["valid"] == true,
		"Serialized request should validate."
	):
		passed = false

	if not _check_internal(
		response_validation["valid"] == true,
		"Serialized response should validate."
	):
		passed = false

	if not _check_internal(
		invalid_json_result["valid"] == false,
		"Malformed serialized JSON should fail validation."
	):
		passed = false

	if not _check_internal(
		array_json_result["valid"] == false,
		"Serialized JSON arrays should fail validation."
	):
		passed = false

	_record_internal_test(
		"Serialized message validation",
		passed
	)


func _test_version_compatibility() -> void:
	var passed: bool = true

	var version_1_0: bool = (
		CONTRACT.is_compatible_version(
			"1.0"
		)
	)

	if not _check_internal(
		version_1_0,
		"Contract version 1.0 should be compatible."
	):
		passed = false

	var version_1_1: bool = (
		CONTRACT.is_compatible_version(
			"1.1"
		)
	)

	if not _check_internal(
		version_1_1,
		"Contract version 1.1 should be compatible."
	):
		passed = false

	var version_1_99: bool = (
		CONTRACT.is_compatible_version(
			"1.99"
		)
	)

	if not _check_internal(
		version_1_99,
		"Contract version 1.99 should be compatible."
	):
		passed = false

	var version_2_0: bool = (
		CONTRACT.is_compatible_version(
			"2.0"
		)
	)

	if not _check_internal(
		not version_2_0,
		"Major version 2 should be rejected."
	):
		passed = false

	var version_0_15: bool = (
		CONTRACT.is_compatible_version(
			"0.15"
		)
	)

	if not _check_internal(
		not version_0_15,
		"Major version 0 should be rejected."
	):
		passed = false

	var empty_version: bool = (
		CONTRACT.is_compatible_version(
			""
		)
	)

	if not _check_internal(
		not empty_version,
		"Empty version should be rejected."
	):
		passed = false

	_record_internal_test(
		"Version compatibility",
		passed
	)


func _test_contract_accessors() -> void:
	var passed: bool = true

	var contract_version: String = (
		CONTRACT.get_contract_version()
	)

	if not _check_internal(
		contract_version == "1.0",
		"Contract accessor should return version 1.0."
	):
		passed = false

	var protocol_name: String = (
		CONTRACT.get_protocol_name()
	)

	if not _check_internal(
		protocol_name == "strontium.rag",
		"Protocol accessor should return strontium.rag."
	):
		passed = false

	_record_internal_test(
		"Contract accessors",
		passed
	)


func _test_request_id_generation() -> void:
	var first_request: Dictionary = (
		CONTRACT.create_request(
			"initialize"
		)
	)

	var second_request: Dictionary = (
		CONTRACT.create_request(
			"initialize"
		)
	)

	var passed: bool = true

	var first_id: String = str(
		first_request["request_id"]
	)

	if not _check_internal(
		not first_id.is_empty(),
		"First request should have a generated request ID."
	):
		passed = false

	var second_id: String = str(
		second_request["request_id"]
	)

	if not _check_internal(
		not second_id.is_empty(),
		"Second request should have a generated request ID."
	):
		passed = false

	if not _check_internal(
		first_id != second_id,
		"Generated request IDs should be unique."
	):
		passed = false

	if not _check_internal(
		first_id.begins_with("req-"),
		"Generated request ID should use the req- prefix."
	):
		passed = false

	_record_internal_test(
		"Request ID generation",
		passed
	)
