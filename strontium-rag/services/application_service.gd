extends Node

signal initialized
signal shutdown_started
signal shutdown_completed


var initialized_state: bool = false
var shutting_down: bool = false


func initialize() -> void:
	if initialized_state:
		return

	shutting_down = false
	initialized_state = true
	initialized.emit()


func shutdown() -> void:
	if shutting_down:
		return

	shutting_down = true
	shutdown_started.emit()

	initialized_state = false
	shutdown_completed.emit()


func is_initialized() -> bool:
	return initialized_state


func is_shutting_down() -> bool:
	return shutting_down
