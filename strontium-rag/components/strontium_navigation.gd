class_name StrontiumNavigation
extends Control


var navigation_service: Node
var screen_registry: ScreenRegistry

var destination_buttons: Dictionary = {}

var navigation_column: VBoxContainer
var title_label: Label
var section_label: Label


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_build_navigation()


func configure(
	service: Node,
	registry: ScreenRegistry
) -> void:
	navigation_service = service
	screen_registry = registry

	if navigation_service != null:
		if not navigation_service.navigation_changed.is_connected(
			_on_navigation_changed
		):
			navigation_service.navigation_changed.connect(
				_on_navigation_changed
			)

	_refresh_destinations()


func _build_navigation() -> void:
	_clear_navigation()

	var background := Panel.new()
	background.name = "NavigationBackground"
	background.mouse_filter = Control.MOUSE_FILTER_IGNORE
	background.set_anchors_and_offsets_preset(
		Control.PRESET_FULL_RECT
	)

	var background_style := StyleBoxFlat.new()

	background_style.bg_color = (
		StrontiumTokens.BACKGROUND_SECONDARY
	)

	background_style.border_color = (
		StrontiumTokens.BORDER_SUBTLE
	)

	background_style.set_border_width(
		SIDE_RIGHT,
		StrontiumTokens.BORDER_WIDTH_SUBTLE
	)

	background.add_theme_stylebox_override(
		"panel",
		background_style
	)

	add_child(background)
	move_child(background, 0)

	var margin := MarginContainer.new()
	margin.name = "NavigationMargin"
	margin.mouse_filter = Control.MOUSE_FILTER_IGNORE
	margin.set_anchors_and_offsets_preset(
		Control.PRESET_FULL_RECT
	)

	margin.add_theme_constant_override(
		"margin_left",
		StrontiumTokens.SPACE_MD
	)

	margin.add_theme_constant_override(
		"margin_right",
		StrontiumTokens.SPACE_MD
	)

	margin.add_theme_constant_override(
		"margin_top",
		StrontiumTokens.SPACE_XL
	)

	margin.add_theme_constant_override(
		"margin_bottom",
		StrontiumTokens.SPACE_XL
	)

	add_child(margin)

	navigation_column = VBoxContainer.new()
	navigation_column.name = "NavigationColumn"

	navigation_column.add_theme_constant_override(
		"separation",
		StrontiumTokens.SPACE_SM
	)

	margin.add_child(navigation_column)

	title_label = Label.new()
	title_label.name = "NavigationTitle"
	title_label.text = "STRONTIUM"
	title_label.mouse_filter = Control.MOUSE_FILTER_IGNORE

	title_label.add_theme_font_size_override(
		"font_size",
		StrontiumTokens.FONT_SIZE_HEADING_SMALL
	)

	title_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_PRIMARY
	)

	navigation_column.add_child(title_label)

	section_label = Label.new()
	section_label.name = "NavigationSection"
	section_label.text = "WORKSPACE"
	section_label.mouse_filter = Control.MOUSE_FILTER_IGNORE

	section_label.add_theme_font_size_override(
		"font_size",
		StrontiumTokens.FONT_SIZE_CAPTION
	)

	section_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_MUTED
	)

	navigation_column.add_child(section_label)

	var spacer := Control.new()
	spacer.name = "SectionSpacer"
	spacer.custom_minimum_size = Vector2(
		0,
		StrontiumTokens.SPACE_SM
	)
	spacer.mouse_filter = Control.MOUSE_FILTER_IGNORE

	navigation_column.add_child(spacer)

	_refresh_destinations()


func _refresh_destinations() -> void:
	if navigation_column == null:
		return

	if screen_registry == null:
		return

	for child in destination_buttons.values():
		if is_instance_valid(child):
			child.queue_free()

	destination_buttons.clear()

	var destinations: Array[String] = (
		screen_registry.get_destinations()
	)

	for destination in destinations:
		var button := StrontiumNavButton.new()

		button.name = destination + "NavigationButton"

		button.setup(
			destination,
			_format_destination_name(destination)
		)

		button.destination_selected.connect(
			_on_destination_selected
		)

		destination_buttons[destination] = button
		navigation_column.add_child(button)

	if navigation_service != null:
		var current: String = (
			navigation_service.get_current_destination()
		)

		if destination_buttons.has(current):
			var active_button: StrontiumNavButton = (
				destination_buttons[current]
			)

			active_button.set_active(true)


func _format_destination_name(destination: String) -> String:
	return destination.replace("_", " ").to_upper()


func _on_destination_selected(destination: String) -> void:
	if navigation_service == null:
		return

	navigation_service.navigate_to(destination)


func _on_navigation_changed(
	_previous_destination: String,
	current_destination: String
) -> void:
	for destination in destination_buttons:
		var button: StrontiumNavButton = (
			destination_buttons[destination]
		)

		button.set_active(
			destination == current_destination
		)


func _clear_navigation() -> void:
	for child in get_children():
		child.queue_free()

	destination_buttons.clear()
