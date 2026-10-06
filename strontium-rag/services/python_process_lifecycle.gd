class_name StrontiumPythonProcessLifecycle
extends Node


signal state_changed(state: String)
signal process_started(process_id: int)
signal process_terminated(process_id: int, exit_code: int)
signal process_failed(message: String)
signal communication_changed(connected: bool)
signal restart_attempted(attempt: int)


const STATE_UNINITIALIZED: String = "UNINITIALIZED"
const STATE_UNAVAILABLE: String = "UNAVAILABLE"
const STATE_STOPPED: String = "STOPPED"
const STATE_STARTING: String = "STARTING"
const STATE_RUNNING: String = "RUNNING"
const STATE_STOPPING: String = "STOPPING"
const STATE_TERMINATED: String = "TERMINATED"
const STATE_FAILED: String = "FAILED"


const DEFAULT_STARTUP_GRACE_SECONDS: float = 0.20
const DEFAULT_MAX_AUTO_RESTARTS: int = 3


var state: String = STATE_UNINITIALIZED

var python_executable: String = ""
var python_prefix_arguments: PackedStringArray = PackedStringArray()
var configured_process_arguments: PackedStringArray = PackedStringArray()

var python_available: bool = false
var python_version_output: String = ""

var process_id: int = -1

var communication_established: bool = false

var auto_restart: bool = false
var max_auto_restarts: int = DEFAULT_MAX_AUTO_RESTARTS
var restart_count: int = 0

var startup_grace_seconds: float = (
	DEFAULT_STARTUP_GRACE_SECONDS
)

var last_error: String = ""
var last_exit_code: int = -1

var shutting_down: bool = false

var _startup_started_msec: int = 0
var _manual_stop_requested: bool = false


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS


func configure(
	python_executable_path: String = "",
	process_arguments: PackedStringArray = PackedStringArray(),
	enable_auto_restart: bool = false,
	restart_limit: int = DEFAULT_MAX_AUTO_RESTARTS,
	startup_grace_period: float = DEFAULT_STARTUP_GRACE_SECONDS
) -> bool:
	if is_running():
		last_error = (
		"Python process must be stopped before reconfiguration."
		)

		process_failed.emit(
			last_error
		)

		return false

	shutting_down = false

	python_executable = (
		python_executable_path.strip_edges()
	)

	configured_process_arguments = (
		process_arguments.duplicate()
	)

	auto_restart = enable_auto_restart

	if restart_limit < 0:
		max_auto_restarts = 0
	else:
		max_auto_restarts = restart_limit

	if startup_grace_period < 0.0:
		startup_grace_seconds = 0.0
	else:
		startup_grace_seconds = startup_grace_period

	python_prefix_arguments = PackedStringArray()

	python_available = false
	python_version_output = ""

	process_id = -1
	communication_established = false
	restart_count = 0
	last_error = ""
	last_exit_code = -1
	_manual_stop_requested = false
	_startup_started_msec = 0

	_set_state(
		STATE_STOPPED
	)

	return true


func detect_python() -> bool:
	if is_running():
		last_error = (
			"Python process must be stopped before detection."
		)

		process_failed.emit(
			last_error
		)

		return false

	var candidates: Array[String] = []

	if OS.has_environment(
		"STRONTIUM_PYTHON_EXECUTABLE"
	):
		var environment_value: String = (
			OS.get_environment(
				"STRONTIUM_PYTHON_EXECUTABLE"
			)
		).strip_edges()

		if not environment_value.is_empty():
			candidates.append(
				environment_value
			)

	var configured_setting: Variant = (
		ProjectSettings.get_setting(
			"strontium/python/executable",
			""
		)
	)

	if configured_setting is String:
		var configured_path: String = (
			configured_setting.strip_edges()
		)

		if not configured_path.is_empty():
			if configured_path not in candidates:
				candidates.append(
					configured_path
				)

	if not python_executable.is_empty():
		if python_executable not in candidates:
			candidates.append(
				python_executable
			)

	var default_candidates: Array[String] = [
		"python",
		"python3",
		"py"
	]

	for candidate in default_candidates:
		if candidate not in candidates:
			candidates.append(
				candidate
			)

	for candidate in candidates:
		var resolved_executable: String = (
			_resolve_executable_path(candidate)
		)

		if resolved_executable.is_empty():
			continue

		var output: Array = []

		var probe_arguments: PackedStringArray = (
			PackedStringArray([
				"--version"
			])
		)

		var exit_code: int = OS.execute(
			resolved_executable,
			probe_arguments,
			output,
			true,
			false
		)

		if exit_code == 0:
			_set_python_executable(
				resolved_executable
			)

			python_available = true
			python_version_output = ""

			if not output.is_empty():
				python_version_output = str(
					output[0]
				).strip_edges()

			last_error = ""
			last_exit_code = 0

			_set_state(
				STATE_STOPPED
			)

			return true

	python_available = false
	python_version_output = ""
	python_executable = ""
	python_prefix_arguments = PackedStringArray()

	last_error = (
		"Python executable could not be detected."
	)

	_set_state(
		STATE_UNAVAILABLE
	)

	return false


func start_python(
	process_arguments: PackedStringArray = PackedStringArray()
) -> bool:
	shutting_down = false

	if is_running():
		return true

	if not python_available:
		if not detect_python():
			return false

	if python_executable.is_empty():
		last_error = (
			"Python executable is unavailable."
		)

		_set_state(
			STATE_FAILED
		)

		process_failed.emit(
			last_error
		)

		return false

	if not process_arguments.is_empty():
		configured_process_arguments = (
			process_arguments.duplicate()
		)

	var final_arguments: PackedStringArray = (
		_build_process_arguments()
	)

	communication_established = false
	_manual_stop_requested = false
	last_error = ""
	last_exit_code = -1

	_set_state(
		STATE_STARTING
	)

	_startup_started_msec = Time.get_ticks_msec()

	var created_process_id: int = OS.create_process(
		python_executable,
		final_arguments,
		false
	)

	if created_process_id < 0:
		process_id = -1

		last_error = (
			"Godot could not create the Python process."
		)

		_set_state(
			STATE_FAILED
		)

		process_failed.emit(
			last_error
		)

		return false

	process_id = created_process_id

	process_started.emit(
		process_id
	)

	return true


func stop_python() -> bool:
	auto_restart = false
	_manual_stop_requested = true

	if process_id < 0:
		communication_established = false

		_set_state(
			STATE_STOPPED
		)

		return true

	_set_state(
		STATE_STOPPING
	)

	var target_process_id: int = process_id

	var kill_result: Error = OS.kill(
		target_process_id
	)

	if kill_result != OK:
		_manual_stop_requested = false

		last_error = (
			"Godot could not stop the Python process."
		)

		_set_state(
			STATE_FAILED
		)

		process_failed.emit(
			last_error
		)

		return false

	process_id = -1
	communication_established = false
	last_exit_code = -1

	_set_state(
		STATE_STOPPED
	)

	return true


func restart_python() -> bool:
	if shutting_down:
		return false

	var restart_arguments: PackedStringArray = (
		configured_process_arguments.duplicate()
	)

	if is_running():
		if not stop_python():
			return false

	restart_count += 1

	restart_attempted.emit(
		restart_count
	)

	_manual_stop_requested = false

	return start_python(
		restart_arguments
	)


func shutdown() -> void:
	shutting_down = true
	auto_restart = false

	stop_python()


func set_auto_restart(
	enabled: bool,
	restart_limit: int = DEFAULT_MAX_AUTO_RESTARTS
) -> void:
	auto_restart = enabled

	if restart_limit < 0:
		max_auto_restarts = 0
	else:
		max_auto_restarts = restart_limit


func set_communication_established(
	connected: bool
) -> bool:
	if connected:
		if not is_running():
			last_error = (
				"Communication cannot be established while Python is not running."
			)

			return false

	var changed: bool = (
		communication_established != connected
	)

	communication_established = connected

	if changed:
		communication_changed.emit(
			communication_established
		)

	return true


func clear_communication_state() -> void:
	set_communication_established(
		false
	)


func is_running() -> bool:
	if process_id < 0:
		return false

	return OS.is_process_running(
		process_id
	)


func is_python_available() -> bool:
	return python_available


func is_communication_established() -> bool:
	return communication_established


func get_state() -> String:
	return state


func get_python_executable() -> String:
	return python_executable


func get_python_version_output() -> String:
	return python_version_output


func get_process_id() -> int:
	return process_id


func get_restart_count() -> int:
	return restart_count


func get_last_error() -> String:
	return last_error


func get_last_exit_code() -> int:
	return last_exit_code


func get_status() -> Dictionary:
	return {
		"state": state,
		"python_available": python_available,
		"python_executable": python_executable,
		"python_version": python_version_output,
		"process_id": process_id,
		"process_running": is_running(),
		"communication_established": communication_established,
		"auto_restart": auto_restart,
		"max_auto_restarts": max_auto_restarts,
		"restart_count": restart_count,
		"startup_grace_seconds": startup_grace_seconds,
		"last_error": last_error,
		"last_exit_code": last_exit_code,
		"shutting_down": shutting_down
	}


func _process(_delta: float) -> void:
	if process_id < 0:
		return

	if OS.is_process_running(
		process_id
	):
		if state == STATE_STARTING:
			var elapsed_msec: int = (
				Time.get_ticks_msec()
				- _startup_started_msec
			)

			var grace_msec: int = int(
				startup_grace_seconds * 1000.0
			)

			if elapsed_msec >= grace_msec:
				_set_state(
					STATE_RUNNING
				)

		return

	_handle_process_termination()


func _handle_process_termination() -> void:
	var terminated_process_id: int = process_id

	var exit_code: int = OS.get_process_exit_code(
		terminated_process_id
	)

	var process_was_starting: bool = (
		state == STATE_STARTING
	)

	var was_manual_stop: bool = (
		_manual_stop_requested
	)

	process_id = -1
	communication_established = false
	last_exit_code = exit_code
	_manual_stop_requested = false

	process_terminated.emit(
		terminated_process_id,
		exit_code
	)

	if was_manual_stop:
		_set_state(
			STATE_STOPPED
		)

		return

	if process_was_starting:
		last_error = (
			"Python process terminated during initialization."
		)

		_set_state(
			STATE_FAILED
		)

		process_failed.emit(
			last_error
		)
	else:
		last_error = (
			"Python process terminated unexpectedly."
		)

		_set_state(
			STATE_TERMINATED
		)

	if auto_restart and not shutting_down:
		if restart_count < max_auto_restarts:
			restart_count += 1

			restart_attempted.emit(
				restart_count
			)

			call_deferred(
				"_restart_after_termination"
			)
		else:
			auto_restart = false


func _restart_after_termination() -> void:
	if shutting_down:
		return

	if not auto_restart:
		return

	start_python()


func _build_process_arguments() -> PackedStringArray:
	var final_arguments: PackedStringArray = (
		PackedStringArray()
	)

	for argument in python_prefix_arguments:
		final_arguments.append(
			argument
		)

	for argument in configured_process_arguments:
		final_arguments.append(
			argument
		)

	return final_arguments


func _resolve_executable_path(
	candidate: String
) -> String:
	var normalized_candidate: String = (
		candidate.strip_edges()
	)

	if normalized_candidate.is_empty():
		return ""

	var candidate_file: FileAccess = null

	if FileAccess.file_exists(
		normalized_candidate
	):
		return normalized_candidate

	var resolver: String = ""

	if OS.get_name() == "Windows":
		resolver = "where.exe"
	else:
		resolver = "which"

	var output: Array = []

	var resolver_arguments: PackedStringArray = (
		PackedStringArray([
			normalized_candidate
		])
	)

	var exit_code: int = OS.execute(
		resolver,
		resolver_arguments,
		output,
		true,
		false
	)

	if exit_code != 0:
		return ""

	if output.is_empty():
		return ""

	var output_text: String = str(
		output[0]
	)

	var output_lines: PackedStringArray = (
		output_text.split(
			"\n",
			false
		)
	)

	for line in output_lines:
		var resolved_path: String = (
			line.strip_edges()
		)

		if resolved_path.is_empty():
			continue

		if OS.get_name() == "Windows":
			if resolved_path.ends_with(
				".exe"
			):
				candidate_file = FileAccess.open(
					resolved_path,
					FileAccess.READ
				)

				if candidate_file != null:
					candidate_file.close()
					return resolved_path
		else:
			candidate_file = FileAccess.open(
				resolved_path,
				FileAccess.READ
			)

			if candidate_file != null:
				candidate_file.close()
				return resolved_path

	return ""


func _set_python_executable(
	executable_path: String
) -> void:
	python_executable = executable_path

	python_prefix_arguments = (
		PackedStringArray()
	)

	var executable_name: String = (
		executable_path.get_file().to_lower()
	)

	if executable_name == "py":
		python_prefix_arguments.append(
			"-3"
		)
	elif executable_name == "py.exe":
		python_prefix_arguments.append(
			"-3"
		)


func _set_state(
	new_state: String
) -> void:
	if state == new_state:
		return

	state = new_state

	state_changed.emit(
		state
	)
