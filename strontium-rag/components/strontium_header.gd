class_name StrontiumHeader
extends Control


signal status_changed(status: String)


var title_label: Label
var subtitle_label: Label
var status_indicator: StrontiumStatusIndicator
var spectrum: StrontiumSpectrum


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_build_header()


func _build_header() -> void:
	_create_background()
	_create_accent()
	_create_content()


func _create_background() -> void:
	var background := Panel.new()
	background.name = "HeaderBackground"
	background.mouse_filter = Control.MOUSE_FILTER_IGNORE
	background.set_anchors_and_offsets_preset(
		Control.PRESET_FULL_RECT
	)

	var style := StyleBoxFlat.new()

	style.bg_color = StrontiumTokens.BACKGROUND_SECONDARY
	style.border_color = StrontiumTokens.BORDER_SUBTLE

	style.set_border_width(
		SIDE_BOTTOM,
		StrontiumTokens.BORDER_WIDTH_SUBTLE
	)

	background.add_theme_stylebox_override(
		"panel",
		style
	)

	add_child(background)
	move_child(background, 0)


func _create_accent() -> void:
	var existing_accent := get_node_or_null(
		"HeaderAccent"
	)

	if existing_accent != null:
		existing_accent.visible = false
		existing_accent.mouse_filter = (
			Control.MOUSE_FILTER_IGNORE
		)

	spectrum = StrontiumSpectrum.new()
	spectrum.name = "HeaderSpectrum"
	spectrum.mouse_filter = Control.MOUSE_FILTER_IGNORE

	spectrum.animated = true
	spectrum.animation_speed = 0.045
	spectrum.intensity = 0.85
	spectrum.line_height = 2.0

	spectrum.anchor_left = 0.0
	spectrum.anchor_top = 0.0
	spectrum.anchor_right = 1.0
	spectrum.anchor_bottom = 0.0

	spectrum.offset_left = 0.0
	spectrum.offset_top = 0.0
	spectrum.offset_right = 0.0
	spectrum.offset_bottom = 2.0

	add_child(spectrum)


func _create_content() -> void:
	var margin := MarginContainer.new()
	margin.name = "HeaderMargin"
	margin.mouse_filter = Control.MOUSE_FILTER_IGNORE

	margin.set_anchors_and_offsets_preset(
		Control.PRESET_FULL_RECT
	)

	margin.add_theme_constant_override(
		"margin_left",
		StrontiumTokens.SPACE_XL
	)

	margin.add_theme_constant_override(
		"margin_right",
		StrontiumTokens.SPACE_XL
	)

	margin.add_theme_constant_override(
		"margin_top",
		StrontiumTokens.SPACE_SM
	)

	margin.add_theme_constant_override(
		"margin_bottom",
		StrontiumTokens.SPACE_SM
	)

	add_child(margin)

	var row := HBoxContainer.new()
	row.name = "HeaderRow"
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.set_anchors_and_offsets_preset(
		Control.PRESET_FULL_RECT
	)

	margin.add_child(row)

	var identity := VBoxContainer.new()
	identity.name = "Identity"
	identity.mouse_filter = Control.MOUSE_FILTER_IGNORE
	identity.custom_minimum_size = Vector2(260, 0)

	row.add_child(identity)

	title_label = Label.new()
	title_label.name = "Title"
	title_label.text = "STRONTIUM RAG"
	title_label.mouse_filter = Control.MOUSE_FILTER_IGNORE

	title_label.add_theme_font_size_override(
		"font_size",
		StrontiumTokens.FONT_SIZE_HEADING_SMALL
	)

	title_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_PRIMARY
	)

	identity.add_child(title_label)

	subtitle_label = Label.new()
	subtitle_label.name = "Subtitle"
	subtitle_label.text = "STRONTIUM LABS // LABORATORY"
	subtitle_label.mouse_filter = Control.MOUSE_FILTER_IGNORE

	subtitle_label.add_theme_font_size_override(
		"font_size",
		StrontiumTokens.FONT_SIZE_CAPTION
	)

	subtitle_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_MUTED
	)

	identity.add_child(subtitle_label)

	var spacer := Control.new()
	spacer.name = "HeaderSpacer"
	spacer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL

	row.add_child(spacer)

	status_indicator = StrontiumStatusIndicator.new()
	status_indicator.name = "StatusIndicator"

	row.add_child(status_indicator)


func set_status(
	status: String,
	color: Color
) -> void:
	if status_indicator == null:
		return

	status_indicator.set_status_color(
		status,
		color
	)

	status_changed.emit(status)


func set_title(
	title: String,
	subtitle: String = ""
) -> void:
	if title_label != null:
		title_label.text = title

	if subtitle_label != null:
		subtitle_label.text = subtitle
