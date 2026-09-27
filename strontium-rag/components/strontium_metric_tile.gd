class_name StrontiumMetricTile
extends PanelContainer


signal metric_pressed


const DEFAULT_WIDTH: float = 220.0
const DEFAULT_HEIGHT: float = 120.0


var title_label: Label
var value_label: Label
var detail_label: Label
var accent_line: ColorRect


@export var metric_title: String = "Metric"
@export var metric_value: String = "0"
@export var metric_detail: String = ""
@export var accent_color: Color = Color(0.35, 0.85, 1.0, 1.0)
@export var interactive: bool = false
@export var glow_enabled: bool = true


func _ready() -> void:
	custom_minimum_size = Vector2(
		DEFAULT_WIDTH,
		DEFAULT_HEIGHT
	)

	mouse_filter = Control.MOUSE_FILTER_STOP

	_build_component()
	_update_component()


func _build_component() -> void:
	var root: VBoxContainer = VBoxContainer.new()
	root.name = "MetricContent"
	root.set_anchors_and_offsets_preset(
		Control.PRESET_FULL_RECT
	)
	root.position = Vector2(16.0, 14.0)
	root.size = Vector2(
		maxf(0.0, size.x - 32.0),
		maxf(0.0, size.y - 28.0)
	)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(root)

	accent_line = ColorRect.new()
	accent_line.name = "AccentLine"
	accent_line.custom_minimum_size = Vector2(
		0.0,
		3.0
	)
	accent_line.color = accent_color
	accent_line.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(accent_line)

	title_label = Label.new()
	title_label.name = "Title"
	title_label.text = metric_title
	title_label.modulate = (
		StrontiumTokens.TEXT_SECONDARY
	)
	title_label.add_theme_font_size_override(
		"font_size",
		13
	)
	title_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(title_label)

	value_label = Label.new()
	value_label.name = "Value"
	value_label.text = metric_value
	value_label.modulate = (
		StrontiumTokens.TEXT_PRIMARY
	)
	value_label.add_theme_font_size_override(
		"font_size",
		30
	)
	value_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(value_label)

	detail_label = Label.new()
	detail_label.name = "Detail"
	detail_label.text = metric_detail
	detail_label.modulate = (
		StrontiumTokens.TEXT_SECONDARY
	)
	detail_label.add_theme_font_size_override(
		"font_size",
		12
	)
	detail_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(detail_label)


func _update_component() -> void:
	if title_label == null:
		return

	title_label.text = metric_title
	value_label.text = metric_value
	detail_label.text = metric_detail
	accent_line.color = accent_color

	if interactive:
		mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	else:
		mouse_default_cursor_shape = Control.CURSOR_ARROW


func set_metric(
	title: String,
	value: String,
	detail: String = ""
) -> void:
	metric_title = title
	metric_value = value
	metric_detail = detail
	_update_component()


func set_metric_title(
	title: String
) -> void:
	metric_title = title
	_update_component()


func set_metric_value(
	value: String
) -> void:
	metric_value = value
	_update_component()


func set_metric_detail(
	detail: String
) -> void:
	metric_detail = detail
	_update_component()


func set_accent_color(
	color: Color
) -> void:
	accent_color = color
	_update_component()


func set_interactive(
	enabled: bool
) -> void:
	interactive = enabled
	_update_component()


func _gui_input(
	event: InputEvent
) -> void:
	if not interactive:
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
		metric_pressed.emit()
