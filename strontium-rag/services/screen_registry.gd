class_name ScreenRegistry
extends Node


signal registry_changed


const HOME: String = "home"
const INGEST: String = "ingest"
const KNOWLEDGE_BASE: String = "knowledge_base"
const CHAT: String = "chat"
const EVALUATION: String = "evaluation"
const SETTINGS: String = "settings"
const DIAGNOSTICS: String = "diagnostics"


const DEFAULT_DESTINATIONS: Array[String] = [
	HOME,
	INGEST,
	KNOWLEDGE_BASE,
	CHAT,
	EVALUATION,
	SETTINGS,
	DIAGNOSTICS
]


var destinations: Dictionary = {}
var initialized: bool = false


func _ready() -> void:
	call_deferred("initialize")


func initialize() -> void:
	if initialized:
		return

	_register_default_destinations()

	initialized = true

	registry_changed.emit()


func _register_default_destinations() -> void:
	destinations.clear()

	register_destination(
		HOME,
		"Home",
		"Strontium RAG command center",
		"HOME",
		"res://scenes/home.tscn"
	)

	register_destination(
		INGEST,
		"Ingest",
		"Document ingestion workspace",
		"DATABASE",
		""
	)

	register_destination(
		KNOWLEDGE_BASE,
		"Knowledge Base",
		"Documents, metadata, and stored knowledge",
		"DATABASE",
		""
	)

	register_destination(
		CHAT,
		"Chat",
		"Conversation and retrieval workspace",
		"CHAT",
		""
	)

	register_destination(
		EVALUATION,
		"Evaluation",
		"RAG evaluation and evidence",
		"ACTIVITY",
		""
	)

	register_destination(
		SETTINGS,
		"Settings",
		"Application and system configuration",
		"SETTINGS",
		""
	)

	register_destination(
		DIAGNOSTICS,
		"Diagnostics",
		"System health, logs, and diagnostics",
		"ACTIVITY",
		""
	)


func register_destination(
	destination_id: String,
	title: String,
	subtitle: String,
	icon_name: String,
	scene_path: String = ""
) -> bool:
	if destination_id.is_empty():
		return false

	if title.is_empty():
		return false

	destinations[destination_id] = {
		"id": destination_id,
		"title": title,
		"subtitle": subtitle,
		"icon": icon_name,
		"scene_path": scene_path
	}

	registry_changed.emit()

	return true


func unregister_destination(
	destination_id: String
) -> bool:
	if not destinations.has(destination_id):
		return false

	destinations.erase(destination_id)

	registry_changed.emit()

	return true


func has_destination(
	destination_id: String
) -> bool:
	return destinations.has(destination_id)


func get_destination(
	destination_id: String
) -> Dictionary:
	var definition: Variant = destinations.get(
		destination_id,
		{}
	)

	if definition is Dictionary:
		return definition

	return {}


func get_destinations() -> Array[String]:
	var result: Array[String] = []

	for destination_id in DEFAULT_DESTINATIONS:
		if destinations.has(destination_id):
			result.append(destination_id)

	for destination_id in destinations.keys():
		if destination_id is String and destination_id not in result:
			result.append(destination_id)

	return result


func get_title(
	destination_id: String
) -> String:
	var definition: Dictionary = get_destination(
		destination_id
	)

	return str(
		definition.get(
			"title",
			destination_id
		)
	)


func get_subtitle(
	destination_id: String
) -> String:
	var definition: Dictionary = get_destination(
		destination_id
	)

	return str(
		definition.get(
			"subtitle",
			""
		)
	)


func get_icon(
	destination_id: String
) -> String:
	var definition: Dictionary = get_destination(
		destination_id
	)

	return str(
		definition.get(
			"icon",
			"INFO"
		)
	)


func get_scene_path(
	destination_id: String
) -> String:
	var definition: Dictionary = get_destination(
		destination_id
	)

	return str(
		definition.get(
			"scene_path",
			""
		)
	)


func is_initialized() -> bool:
	return initialized


func clear_registry() -> void:
	destinations.clear()
	initialized = false

	registry_changed.emit()


func reset() -> void:
	clear_registry()
	initialize()
