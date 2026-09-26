extends Node

signal state_changed(previous_state: int, current_state: int)

enum Status {
	STARTING,
	READY,
	ERROR,
	SHUTTING_DOWN
}

var status: int = Status.STARTING
var initialized: bool = false
var message: String = ""


func set_status(new_status: int, new_message: String = "") -> void:
	var previous_status := status
	status = new_status
	message = new_message
	state_changed.emit(previous_status, status)


func mark_starting() -> void:
	initialized = false
	set_status(Status.STARTING, "Strontium RAG is starting.")


func mark_ready() -> void:
	initialized = true
	set_status(Status.READY, "Strontium RAG is ready.")


func mark_error(error_message: String) -> void:
	initialized = false
	set_status(Status.ERROR, error_message)


func begin_shutdown() -> void:
	initialized = false
	set_status(Status.SHUTTING_DOWN, "Strontium RAG is shutting down.")


func get_status_name() -> String:
	return Status.keys()[status]


func is_starting() -> bool:
	return status == Status.STARTING


func is_ready() -> bool:
	return status == Status.READY


func has_error() -> bool:
	return status == Status.ERROR


func is_shutting_down() -> bool:
	return status == Status.SHUTTING_DOWN
