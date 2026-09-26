class_name ScreenRegistry
extends Node


var destinations: Dictionary = {}


func initialize() -> void:
	register_destination("Home", "res://scenes/home.tscn")


func register_destination(destination: String, scene_path: String) -> void:
	if destination.is_empty():
		push_error("Cannot register an empty navigation destination.")
		return

	if scene_path.is_empty():
		push_error("Cannot register an empty scene path.")
		return

	destinations[destination] = scene_path


func unregister_destination(destination: String) -> void:
	if not destinations.has(destination):
		return

	destinations.erase(destination)


func has_destination(destination: String) -> bool:
	return destinations.has(destination)


func get_scene_path(destination: String) -> String:
	if not destinations.has(destination):
		return ""

	return destinations[destination]


func get_destinations() -> Array[String]:
	var result: Array[String] = []

	for destination in destinations.keys():
		result.append(str(destination))

	return result


func clear() -> void:
	destinations.clear()
