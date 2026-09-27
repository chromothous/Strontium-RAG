class_name StrontiumSourceChip
extends Button


signal source_selected(source_id: String)


@export var source_id: String = ""
@export var source_title: String = "Source"
@export var source_type: String = ""
@export var removable: bool = false


func _ready() -> void:
	flat = true
	clip_text = true
	mouse_default_cursor_shape = (
		Control.CURSOR_POINTING_HAND
	)

	_update_text()

	if not pressed.is_connected(
		_on_pressed
	):
		pressed.connect(
			_on_pressed
		)


func _update_text() -> void:
	if source_type.is_empty():
		text = source_title
	else:
		text = (
			source_title
			+ "  •  "
			+ source_type
		)


func set_source(
	id: String,
	title: String,
	type: String = ""
) -> void:
	source_id = id
	source_title = title
	source_type = type

	_update_text()


func get_source_id() -> String:
	return source_id


func get_source_title() -> String:
	return source_title


func get_source_type() -> String:
	return source_type


func set_removable(
	enabled: bool
) -> void:
	removable = enabled
	_update_text()


func _on_pressed() -> void:
	source_selected.emit(
		source_id
	)
