class_name StrontiumDocumentRow
extends PanelContainer


signal document_selected(document_id: String)
signal document_action_requested(
	document_id: String
)


var document_id: String = ""
var document_title: String = ""
var document_source: String = ""
var document_status: String = ""
var document_detail: String = ""


var title_label: Label
var source_label: Label
var status_label: Label
var detail_label: Label
var action_button: Button


@export var selectable: bool = true
@export var show_action_button: bool = true


func _ready() -> void:
	custom_minimum_size = Vector2(
		0.0,
		76.0
	)

	mouse_filter = Control.MOUSE_FILTER_STOP

	_build_component()
	_update_component()


func _build_component() -> void:
	var content: HBoxContainer = (
		HBoxContainer.new()
	)

	content.name = "DocumentContent"
	content.set_anchors_and_offsets_preset(
		Control.PRESET_FULL_RECT
	)
	content.position = Vector2(
		16.0,
		10.0
	)
	content.size = Vector2(
		maxf(0.0, size.x - 32.0),
		maxf(0.0, size.y - 20.0)
	)
	content.mouse_filter = Control.MOUSE_FILTER_IGNORE

	add_child(content)

	var icon_label: Label = Label.new()
	icon_label.name = "DocumentIcon"
	icon_label.text = "DOC"
	icon_label.custom_minimum_size = (
		Vector2(48.0, 0.0)
	)
	icon_label.vertical_alignment = (
		VerticalAlignment.VERTICAL_ALIGNMENT_CENTER
	)
	icon_label.modulate = (
		StrontiumTokens.TEXT_SECONDARY
	)
	icon_label.add_theme_font_size_override(
		"font_size",
		11
	)
	icon_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	content.add_child(icon_label)

	var information: VBoxContainer = (
		VBoxContainer.new()
	)

	information.name = "Information"
	information.size_flags_horizontal = (
		Control.SIZE_EXPAND_FILL
	)
	information.mouse_filter = (
		Control.MOUSE_FILTER_IGNORE
	)
	content.add_child(information)

	title_label = Label.new()
	title_label.name = "Title"
	title_label.text = document_title
	title_label.modulate = (
		StrontiumTokens.TEXT_PRIMARY
	)
	title_label.add_theme_font_size_override(
		"font_size",
		15
	)
	title_label.mouse_filter = (
		Control.MOUSE_FILTER_IGNORE
	)
	information.add_child(title_label)

	source_label = Label.new()
	source_label.name = "Source"
	source_label.text = document_source
	source_label.modulate = (
		StrontiumTokens.TEXT_SECONDARY
	)
	source_label.add_theme_font_size_override(
		"font_size",
		12
	)
	source_label.mouse_filter = (
		Control.MOUSE_FILTER_IGNORE
	)
	information.add_child(source_label)

	detail_label = Label.new()
	detail_label.name = "Detail"
	detail_label.text = document_detail
	detail_label.modulate = (
		StrontiumTokens.TEXT_SECONDARY
	)
	detail_label.add_theme_font_size_override(
		"font_size",
		11
	)
	detail_label.mouse_filter = (
		Control.MOUSE_FILTER_IGNORE
	)
	information.add_child(detail_label)

	status_label = Label.new()
	status_label.name = "Status"
	status_label.text = document_status
	status_label.custom_minimum_size = (
		Vector2(90.0, 0.0)
	)
	status_label.horizontal_alignment = (
		HORIZONTAL_ALIGNMENT_CENTER
	)
	status_label.vertical_alignment = (
		VerticalAlignment.VERTICAL_ALIGNMENT_CENTER
	)
	status_label.modulate = (
		StrontiumTokens.TEXT_SECONDARY
	)
	status_label.mouse_filter = (
		Control.MOUSE_FILTER_IGNORE
	)
	content.add_child(status_label)

	action_button = Button.new()
	action_button.name = "Action"
	action_button.text = "•••"
	action_button.flat = true
	action_button.custom_minimum_size = (
		Vector2(40.0, 40.0)
	)

	action_button.mouse_filter = (
		Control.MOUSE_FILTER_PASS
	)

	action_button.pressed.connect(
		_on_action_pressed
	)

	content.add_child(
		action_button
	)


func _update_component() -> void:
	if title_label == null:
		return

	title_label.text = document_title
	source_label.text = document_source
	status_label.text = document_status
	detail_label.text = document_detail
	action_button.visible = show_action_button

	if selectable:
		mouse_default_cursor_shape = (
			Control.CURSOR_POINTING_HAND
		)
	else:
		mouse_default_cursor_shape = (
			Control.CURSOR_ARROW
		)


func set_document(
	id: String,
	title: String,
	source: String = "",
	status: String = "",
	detail: String = ""
) -> void:
	document_id = id
	document_title = title
	document_source = source
	document_status = status
	document_detail = detail

	_update_component()


func set_selectable(
	enabled: bool
) -> void:
	selectable = enabled
	_update_component()


func set_action_button_visible(
	visible: bool
) -> void:
	show_action_button = visible
	_update_component()


func get_document_id() -> String:
	return document_id


func get_document_title() -> String:
	return document_title


func get_document_source() -> String:
	return document_source


func get_document_status() -> String:
	return document_status


func _gui_input(
	event: InputEvent
) -> void:
	if not selectable:
		return

	var mouse_event: InputEventMouseButton = (
		event as InputEventMouseButton
	)

	if mouse_event == null:
		return

	if (
		mouse_event.button_index
		== MOUSE_BUTTON_LEFT
		and mouse_event.pressed
	):
		document_selected.emit(
			document_id
		)


func _on_action_pressed() -> void:
	document_action_requested.emit(
		document_id
	)
