class_name StrontiumStartupService
extends Node


enum StartupStage {
	LAUNCH,
	CONFIGURATION,
	UI_INITIALIZATION,
	PYTHON_RUNTIME,
	BACKEND_INTEGRATION,
	RAG_INITIALIZATION,
	READY,
	FAILED
}


signal startup_started
signal stage_changed(stage: StartupStage, stage_name: String, detail: String, progress: float)
signal startup_completed
signal startup_failed(stage: StartupStage, detail: String)


const PYTHON_EXECUTABLE_DEFAULT: String = "python"

const STAGE_PROGRESS: Dictionary = {
	StartupStage.LAUNCH: 0.0,
	StartupStage.CONFIGURATION: 10.0,
	StartupStage.UI_INITIALIZATION: 25.0,
	StartupStage.PYTHON_RUNTIME: 45.0,
	StartupStage.BACKEND_INTEGRATION: 65.0,
	StartupStage.RAG_INITIALIZATION: 85.0,
	StartupStage.READY: 100.0
}


var initialized: bool = false
var startup_in_progress: bool = false
var startup_succeeded: bool = false

var configuration_ready: bool = false
var ui_ready: bool = false
var python_available: bool = false
var backend_integration_ready: bool = false
var rag_ready: bool = false

var python_executable: String = ""
var startup_error: String = ""
var current_stage: StartupStage = StartupStage.LAUNCH
var current_stage_name: String = "LAUNCH"
var current_detail: String = ""
var current_progress: float = 0.0


func initialize() -> void:
	if startup_in_progress:
		return

	if initialized:
		return

	startup_in_progress = true
	startup_succeeded = false
	startup_error = ""

	startup_started.emit()

	_run_startup_pipeline()


func _run_startup_pipeline() -> void:
	_set_stage(
		StartupStage.LAUNCH,
		"LAUNCH",
		"Starting Strontium application",
		0.0
	)

	if not _initialize_configuration():
		return

	if not _initialize_ui():
		return

	if not _initialize_python_runtime():
		return

	if not _initialize_backend_integration():
		return

	if not _initialize_rag():
		return

	_complete_startup()


func _initialize_configuration() -> bool:
	_set_stage(
		StartupStage.CONFIGURATION,
		"CONFIGURATION",
		"Loading application configuration",
		10.0
	)

	var project_name: String = str(
		ProjectSettings.get_setting(
			"application/config/name",
			""
		)
	)

	if project_name.is_empty():
		_fail_startup(
			StartupStage.CONFIGURATION,
			"Application configuration is missing the project name"
		)
		return false

	configuration_ready = true

	_set_stage(
		StartupStage.CONFIGURATION,
		"CONFIGURATION",
		"Application configuration loaded",
		20.0
	)

	return true


func _initialize_ui() -> bool:
	_set_stage(
		StartupStage.UI_INITIALIZATION,
		"UI INITIALIZATION",
		"Initializing application interface",
		25.0
	)

	var tree: SceneTree = get_tree()

	if tree == null:
		_fail_startup(
			StartupStage.UI_INITIALIZATION,
			"SceneTree is unavailable"
		)
		return false

	var current_scene: Node = tree.current_scene

	if current_scene == null:
		_fail_startup(
			StartupStage.UI_INITIALIZATION,
			"No current application scene is available"
		)
		return false

	ui_ready = true

	_set_stage(
		StartupStage.UI_INITIALIZATION,
		"UI INITIALIZATION",
		"Application interface initialized",
		35.0
	)

	return true


func _initialize_python_runtime() -> bool:
	_set_stage(
		StartupStage.PYTHON_RUNTIME,
		"PYTHON RUNTIME",
		"Checking Python runtime availability",
		45.0
	)

	var configured_executable: String = str(
		ProjectSettings.get_setting(
			"strontium/python_executable",
			PYTHON_EXECUTABLE_DEFAULT
		)
	)

	if configured_executable.is_empty():
		configured_executable = PYTHON_EXECUTABLE_DEFAULT

	var detected_executable: String = _find_python_executable(
		configured_executable
	)

	if detected_executable.is_empty():
		_fail_startup(
			StartupStage.PYTHON_RUNTIME,
			"Python runtime could not be located"
		)
		return false

	python_executable = detected_executable
	python_available = true

	_set_stage(
		StartupStage.PYTHON_RUNTIME,
		"PYTHON RUNTIME",
		"Python runtime detected: " + python_executable,
		55.0
	)

	return true


func _find_python_executable(configured_executable: String) -> String:
	if _test_python_executable(configured_executable):
		return configured_executable

	if OS.get_name() == "Windows":
		if configured_executable != "py":
			if _test_python_executable("py"):
				return "py"

	return ""


func _test_python_executable(executable: String) -> bool:
	var output: Array[String] = []

	var arguments: PackedStringArray = PackedStringArray([
		"--version"
	])

	var exit_code: int = OS.execute(
		executable,
		arguments,
		output,
		true,
		false
	)

	return exit_code == 0


func _initialize_backend_integration() -> bool:
	_set_stage(
		StartupStage.BACKEND_INTEGRATION,
		"BACKEND INTEGRATION",
		"Preparing the Python integration boundary",
		65.0
	)

	backend_integration_ready = false

	_set_stage(
		StartupStage.BACKEND_INTEGRATION,
		"BACKEND INTEGRATION",
		"Python integration boundary prepared",
		72.0
	)

	return true


func _initialize_rag() -> bool:
	_set_stage(
		StartupStage.RAG_INITIALIZATION,
		"RAG INITIALIZATION",
		"Preparing Strontium RAG startup handoff",
		85.0
	)

	rag_ready = false

	_set_stage(
		StartupStage.RAG_INITIALIZATION,
		"RAG INITIALIZATION",
		"Strontium RAG startup handoff prepared",
		92.0
	)

	return true


func _complete_startup() -> void:
	current_stage = StartupStage.READY
	current_stage_name = "READY"
	current_detail = "Application startup pipeline prepared"
	current_progress = 100.0

	initialized = true
	startup_in_progress = false
	startup_succeeded = true

	stage_changed.emit(
		current_stage,
		current_stage_name,
		current_detail,
		current_progress
	)

	startup_completed.emit()


func _fail_startup(stage: StartupStage, detail: String) -> void:
	current_stage = StartupStage.FAILED
	current_stage_name = "FAILED"
	current_detail = detail
	current_progress = float(STAGE_PROGRESS.get(stage, 0.0))

	startup_error = detail
	startup_in_progress = false
	startup_succeeded = false

	stage_changed.emit(
		StartupStage.FAILED,
		"FAILED",
		detail,
		current_progress
	)

	startup_failed.emit(stage, detail)


func _set_stage(
	stage: StartupStage,
	stage_name: String,
	detail: String,
	progress: float
) -> void:
	current_stage = stage
	current_stage_name = stage_name
	current_detail = detail
	current_progress = clampf(progress, 0.0, 100.0)

	stage_changed.emit(
		stage,
		stage_name,
		detail,
		current_progress
	)


func get_startup_state() -> Dictionary:
	return {
		"initialized": initialized,
		"startup_in_progress": startup_in_progress,
		"startup_succeeded": startup_succeeded,
		"configuration_ready": configuration_ready,
		"ui_ready": ui_ready,
		"python_available": python_available,
		"backend_integration_ready": backend_integration_ready,
		"rag_ready": rag_ready,
		"python_executable": python_executable,
		"startup_error": startup_error,
		"current_stage": current_stage,
		"current_stage_name": current_stage_name,
		"current_detail": current_detail,
		"current_progress": current_progress
	}


func is_ready() -> bool:
	return initialized and startup_succeeded


func is_python_available() -> bool:
	return python_available


func is_backend_integration_ready() -> bool:
	return backend_integration_ready


func is_rag_ready() -> bool:
	return rag_ready


func get_python_executable() -> String:
	return python_executable


func get_current_stage() -> StartupStage:
	return current_stage


func get_current_stage_name() -> String:
	return current_stage_name


func get_current_detail() -> String:
	return current_detail


func get_current_progress() -> float:
	return current_progress


func get_startup_error() -> String:
	return startup_error


func reset() -> void:
	initialized = false
	startup_in_progress = false
	startup_succeeded = false

	configuration_ready = false
	ui_ready = false
	python_available = false
	backend_integration_ready = false
	rag_ready = false

	python_executable = ""
	startup_error = ""

	current_stage = StartupStage.LAUNCH
	current_stage_name = "LAUNCH"
	current_detail = ""
	current_progress = 0.0
