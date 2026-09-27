class_name StrontiumFooter
extends Control


const FOOTER_HEIGHT := 40.0


var left_label: Label
var destination_label: Label
var status_indicator: StrontiumStatusIndicator


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_configure_layout()
	_build()


func _configure_layout() -> void:
	set_anchors_preset(Control.PRESET_BOTTOM_WIDE)

	offset_left = 0.0
	offset_top = -FOOTER_HEIGHT
	offset_right = 0.0
	offset_bottom = 0.0

	custom_minimum_size = Vector2(0, FOOTER_HEIGHT)


func _build() -> void:
	_create_background()
	_create_content()


func _create_background() -> void:
	var background := Panel.new()
	background.name = "FooterBackground"
	background.mouse_filter = Control.MOUSE_FILTER_IGNORE

	background.set_anchors_and_offsets_preset(
		Control.PRESET_FULL_RECT
	)

	var style := StyleBoxFlat.new()

	style.bg_color = StrontiumTokens.BACKGROUND_SECONDARY
	style.border_color = StrontiumTokens.BORDER_SUBTLE

	style.set_border_width(
		SIDE_TOP,
		StrontiumTokens.BORDER_WIDTH_SUBTLE
	)

	background.add_theme_stylebox_override(
		"panel",
		style
	)

	add_child(background)
	move_child(background, 0)


func _create_content() -> void:
	var margin := MarginContainer.new()
	margin.name = "FooterMargin"
	margin.mouse_filter = Control.MOUSE_FILTER_IGNORE

	margin.set_anchors_and_offsets_preset(
		Control.PRESET_FULL_RECT
	)

	margin.add_theme_constant_override(
		"margin_left",
		StrontiumTokens.SPACE_LG
	)

	margin.add_theme_constant_override(
		"margin_right",
		StrontiumTokens.SPACE_LG
	)

	margin.add_theme_constant_override(
		"margin_top",
		StrontiumTokens.SPACE_XS
	)

	margin.add_theme_constant_override(
		"margin_bottom",
		StrontiumTokens.SPACE_XS
	)

	add_child(margin)

	var row := HBoxContainer.new()
	row.name = "FooterRow"
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE

	margin.add_child(row)

	left_label = Label.new()
	left_label.name = "Identity"
	left_label.text = "STRONTIUM RAG // 0.15.1"
	left_label.mouse_filter = Control.MOUSE_FILTER_IGNORE

	left_label.add_theme_font_size_override(
		"font_size",
		StrontiumTokens.FONT_SIZE_CAPTION
	)

	left_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_MUTED
	)

	row.add_child(left_label)

	var spacer := Control.new()
	spacer.name = "FooterSpacer"
	spacer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL

	row.add_child(spacer)

	destination_label = Label.new()
	destination_label.name = "Destination"
	destination_label.text = "HOME"
	destination_label.mouse_filter = Control.MOUSE_FILTER_IGNORE

	destination_label.add_theme_font_size_override(
		"font_size",
		StrontiumTokens.FONT_SIZE_CAPTION
	)

	destination_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	row.add_child(destination_label)

	var separator := Label.new()
	separator.name = "Separator"
	separator.text = " // "
	separator.mouse_filter = Control.MOUSE_FILTER_IGNORE

	separator.add_theme_font_size_override(
		"font_size",
		StrontiumTokens.FONT_SIZE_CAPTION
	)

	separator.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_MUTED
	)

	row.add_child(separator)

	status_indicator = StrontiumStatusIndicator.new()
	status_indicator.name = "Status"

	row.add_child(status_indicator)

	status_indicator.set_status(
		"READY",
		StrontiumStatusIndicator.StatusType.SUCCESS
	)


func set_destination(destination: String) -> void:
	if destination_label == null:
		return

	destination_label.text = destination.to_upper()


func set_status(
	status: String,
	type: StrontiumStatusIndicator.StatusType
) -> void:
	if status_indicator == null:
		return

	status_indicator.set_status(
		status,
		type
	)


func set_status_color(
	status: String,
	color: Color
) -> void:
	if status_indicator == null:
		return

	status_indicator.set_status_color(
		status,
		color
	)
