class_name DebugService
extends Node


var enabled: bool = true
var messages: Array[String] = []


func initialize() -> void:
	if not enabled:
		return

	write("DebugService initialized.")


func shutdown() -> void:
	if not enabled:
		return

	write("DebugService shutting down.")


func write(message: String) -> void:
	if not enabled:
		return

	messages.append(message)
	print("[DEBUG] " + message)


func is_enabled() -> bool:
	return enabled


func get_messages() -> Array[String]:
	return messages.duplicate()


func clear_messages() -> void:
	messages.clear()
