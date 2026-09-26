class_name StrontiumComponent
extends Control


signal component_initialized
signal component_enabled
signal component_disabled


var initialized: bool = false


func initialize() -> void:
	if initialized:
		return

	initialized = true
	_on_initialize()
	component_initialized.emit()


func enable() -> void:
	if not initialized:
		initialize()

	visible = true
	mouse_filter = Control.MOUSE_FILTER_STOP
	_on_enable()
	component_enabled.emit()


func disable() -> void:
	visible = false
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_on_disable()
	component_disabled.emit()


func is_initialized() -> bool:
	return initialized


func _on_initialize() -> void:
	pass


func _on_enable() -> void:
	pass


func _on_disable() -> void:
	pass
