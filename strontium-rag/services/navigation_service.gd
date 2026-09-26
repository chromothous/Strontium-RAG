extends Node

signal navigation_requested(destination: String)
signal navigation_changed(previous_destination: String, current_destination: String)


var current_destination: String = ""
var previous_destination: String = ""
var current_screen: BaseScreen = null
var content_root: Control = null
var screen_registry: ScreenRegistry = null


func configure(root: Control, registry: ScreenRegistry) -> void:
	content_root = root
	screen_registry = registry


func navigate_to(destination: String) -> void:
	if destination.is_empty():
		return

	if content_root == null:
		push_error("NavigationService is not configured with a ContentRoot.")
		return

	if screen_registry == null:
		push_error("NavigationService is not configured with a ScreenRegistry.")
		return

	if not screen_registry.has_destination(destination):
		push_error("Navigation destination does not exist: " + destination)
		return

	if destination == current_destination and is_instance_valid(current_screen):
		return

	var scene_path: String = screen_registry.get_scene_path(destination)
	var scene_resource: PackedScene = load(scene_path) as PackedScene

	if scene_resource == null:
		push_error("Unable to load navigation scene: " + scene_path)
		return

	var screen: BaseScreen = scene_resource.instantiate() as BaseScreen

	if screen == null:
		push_error("Navigation scene must use BaseScreen as its root: " + scene_path)
		return

	_clear_current_screen()

	content_root.add_child(screen)
	current_screen = screen

	previous_destination = current_destination
	current_destination = destination

	screen.enter()

	navigation_requested.emit(destination)
	navigation_changed.emit(previous_destination, current_destination)


func has_destination(destination: String) -> bool:
	if screen_registry == null:
		return false

	return screen_registry.has_destination(destination)


func has_destination_loaded() -> bool:
	return is_instance_valid(current_screen)


func get_current_destination() -> String:
	return current_destination


func get_previous_destination() -> String:
	return previous_destination


func get_current_screen() -> BaseScreen:
	return current_screen


func get_registered_destinations() -> Array[String]:
	if screen_registry == null:
		return []

	return screen_registry.get_destinations()


func _clear_current_screen() -> void:
	if is_instance_valid(current_screen):
		current_screen.exit()
		current_screen.queue_free()

	current_screen = null
