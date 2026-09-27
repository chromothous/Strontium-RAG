class_name NavigationService
extends Node


signal navigation_changed(
	destination_id: String,
	title: String
)
signal destination_changed(
	destination_id: String,
	title: String,
	subtitle: String
)
signal navigation_started(destination_id: String)
signal navigation_completed(destination_id: String)
signal navigation_failed(
	destination_id: String,
	reason: String
)
signal history_changed


var screen_registry: ScreenRegistry
var workspace: StrontiumWorkspace
var current_destination: String = ""
var previous_destination: String = ""
var navigation_history: Array[String] = []
var history_index: int = -1
var configured: bool = false


func _ready() -> void:
	call_deferred("_attempt_auto_configuration")


func configure(
	target_workspace: Control = null,
	registry: ScreenRegistry = null
) -> void:
	screen_registry = registry

	if target_workspace != null:
		workspace = target_workspace as StrontiumWorkspace

	if workspace == null:
		workspace = _find_workspace()

	configured = (
		screen_registry != null
		and workspace != null
	)


func _attempt_auto_configuration() -> void:
	if configured:
		return

	var current_scene: Node = get_tree().current_scene

	if current_scene == null:
		return

	var registry_node: Node = current_scene.find_child(
		"ScreenRegistry",
		true,
		false
	)

	var workspace_node: Node = current_scene.find_child(
		"ContentRoot",
		true,
		false
	)

	var registry: ScreenRegistry = (
		registry_node as ScreenRegistry
	)

	var target_workspace: StrontiumWorkspace = (
		workspace_node as StrontiumWorkspace
	)

	if registry == null:
		return

	if target_workspace == null:
		return

	configure(
		target_workspace,
		registry
	)


func _find_workspace() -> StrontiumWorkspace:
	var current_scene: Node = get_tree().current_scene

	if current_scene == null:
		return null

	var workspace_node: Node = current_scene.find_child(
		"ContentRoot",
		true,
		false
	)

	return workspace_node as StrontiumWorkspace


func navigate_to(
	destination_id: String
) -> bool:
	if not configured:
		_attempt_auto_configuration()

	if screen_registry == null:
		_fail_navigation(
			destination_id,
			"Screen registry is unavailable"
		)
		return false

	if workspace == null:
		workspace = _find_workspace()

	if workspace == null:
		_fail_navigation(
			destination_id,
			"Navigation workspace is unavailable"
		)
		return false

	if not screen_registry.has_destination(
		destination_id
	):
		_fail_navigation(
			destination_id,
			"Unknown navigation destination: "
			+ destination_id
		)
		return false

	if destination_id == current_destination:
		return true

	var definition: Dictionary = (
		screen_registry.get_destination(
			destination_id
		)
	)

	if definition.is_empty():
		_fail_navigation(
			destination_id,
			"Navigation destination definition is empty"
		)
		return false

	var title: String = str(
		definition.get(
			"title",
			destination_id
		)
	)

	var subtitle: String = str(
		definition.get(
			"subtitle",
			""
		)
	)

	var scene_path: String = str(
		definition.get(
			"scene_path",
			""
		)
	)

	navigation_started.emit(
		destination_id
	)

	var displayed: bool = (
		workspace.display_destination(
			definition,
			scene_path
		)
	)

	if not displayed:
		_fail_navigation(
			destination_id,
			"Destination could not be displayed"
		)
		return false

	previous_destination = current_destination
	current_destination = destination_id

	_record_history(
		destination_id
	)

	navigation_changed.emit(
		destination_id,
		title
	)

	destination_changed.emit(
		destination_id,
		title,
		subtitle
	)

	navigation_completed.emit(
		destination_id
	)

	return true


func navigate(
	destination_id: String
) -> bool:
	return navigate_to(
		destination_id
	)


func go_home() -> bool:
	return navigate_to(
		ScreenRegistry.HOME
	)


func go_back() -> bool:
	return back()


func back() -> bool:
	if screen_registry == null:
		return false

	if workspace == null:
		workspace = _find_workspace()

	if workspace == null:
		return false

	if history_index <= 0:
		return false

	history_index -= 1

	var destination_id: String = (
		navigation_history[
			history_index
		]
	)

	var definition: Dictionary = (
		screen_registry.get_destination(
			destination_id
		)
	)

	if definition.is_empty():
		history_index += 1
		return false

	var scene_path: String = str(
		definition.get(
			"scene_path",
			""
		)
	)

	if not workspace.display_destination(
		definition,
		scene_path
	):
		history_index += 1
		return false

	previous_destination = current_destination
	current_destination = destination_id

	var title: String = (
		screen_registry.get_title(
			destination_id
		)
	)

	var subtitle: String = (
		screen_registry.get_subtitle(
			destination_id
		)
	)

	navigation_changed.emit(
		destination_id,
		title
	)

	destination_changed.emit(
		destination_id,
		title,
		subtitle
	)

	history_changed.emit()

	return true


func forward() -> bool:
	if screen_registry == null:
		return false

	if workspace == null:
		workspace = _find_workspace()

	if workspace == null:
		return false

	if (
		history_index
		>= navigation_history.size() - 1
	):
		return false

	history_index += 1

	var destination_id: String = (
		navigation_history[
			history_index
		]
	)

	var definition: Dictionary = (
		screen_registry.get_destination(
			destination_id
		)
	)

	if definition.is_empty():
		history_index -= 1
		return false

	var scene_path: String = str(
		definition.get(
			"scene_path",
			""
		)
	)

	if not workspace.display_destination(
		definition,
		scene_path
	):
		history_index -= 1
		return false

	previous_destination = current_destination
	current_destination = destination_id

	var title: String = (
		screen_registry.get_title(
			destination_id
		)
	)

	var subtitle: String = (
		screen_registry.get_subtitle(
			destination_id
		)
	)

	navigation_changed.emit(
		destination_id,
		title
	)

	destination_changed.emit(
		destination_id,
		title,
		subtitle
	)

	history_changed.emit()

	return true


func can_go_back() -> bool:
	return history_index > 0


func can_go_forward() -> bool:
	return (
		history_index
		< navigation_history.size() - 1
	)


func get_current_destination() -> String:
	return current_destination


func get_previous_destination() -> String:
	return previous_destination


func get_current_definition() -> Dictionary:
	if screen_registry == null:
		return {}

	if current_destination.is_empty():
		return {}

	return screen_registry.get_destination(
		current_destination
	)


func get_destinations() -> Array[String]:
	if screen_registry == null:
		return []

	return screen_registry.get_destinations()


func get_destination(
	destination_id: String
) -> Dictionary:
	if screen_registry == null:
		return {}

	return screen_registry.get_destination(
		destination_id
	)


func get_destination_title(
	destination_id: String
) -> String:
	if screen_registry == null:
		return destination_id

	return screen_registry.get_title(
		destination_id
	)


func get_destination_subtitle(
	destination_id: String
) -> String:
	if screen_registry == null:
		return ""

	return screen_registry.get_subtitle(
		destination_id
	)


func get_history() -> Array[String]:
	return navigation_history.duplicate()


func clear_history() -> void:
	navigation_history.clear()
	history_index = -1
	history_changed.emit()


func reset_navigation() -> void:
	current_destination = ""
	previous_destination = ""
	clear_history()


func _record_history(
	destination_id: String
) -> void:
	if history_index >= 0:
		if (
			navigation_history[
				history_index
			] == destination_id
		):
			return

	while (
		navigation_history.size()
		> history_index + 1
	):
		navigation_history.pop_back()

	navigation_history.append(
		destination_id
	)

	history_index = (
		navigation_history.size() - 1
	)

	history_changed.emit()


func _fail_navigation(
	destination_id: String,
	reason: String
) -> void:
	navigation_failed.emit(
		destination_id,
		reason
	)
