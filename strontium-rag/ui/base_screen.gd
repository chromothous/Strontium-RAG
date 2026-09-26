class_name BaseScreen
extends Control

signal screen_initialized
signal screen_entered
signal screen_exited


var initialized: bool = false
var active: bool = false


func initialize() -> void:
	if initialized:
		return

	initialized = true
	_on_initialize()
	screen_initialized.emit()


func enter() -> void:
	initialize()

	if active:
		return

	active = true
	_on_enter()
	screen_entered.emit()


func exit() -> void:
	if not active:
		return

	active = false
	_on_exit()
	screen_exited.emit()


func is_initialized() -> bool:
	return initialized


func is_active() -> bool:
	return active


func _on_initialize() -> void:
	pass


func _on_enter() -> void:
	pass


func _on_exit() -> void:
	pass
