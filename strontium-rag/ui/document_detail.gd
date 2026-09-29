class_name StrontiumDocumentDetail
extends Control


signal closed()


const OUTER_MARGIN: int = 32
const PANEL_PADDING: int = 24


var document: Dictionary = {}

var scroll_container: ScrollContainer = null

var identity_value: Label = null
var title_value: Label = null
var source_value: Label = null
var type_value: Label = null
var state_value: Label = null

var metadata_value: Label = null
var preprocessing_value: Label = null
var processing_value: Label = null
var errors_value: Label = null

var chunks_container: VBoxContainer = null


func _ready() -> void:
	set_anchors_and_offsets_preset(
		Control.PRESET_FULL_RECT
	)

	mouse_filter = Control.MOUSE_FILTER_STOP

	_build_interface()


func set_document(
	new_document: Dictionary
) -> void:
	document = new_document.duplicate(
		true
	)

	if is_inside_tree():
		_render_document()


func _build_interface() -> void:
	for child in get_children():
		child.queue_free()

	var background: ColorRect = ColorRect.new()

	background.name = "InspectionBackground"

	background.set_anchors_and_offsets_preset(
		Control.PRESET_FULL_RECT
	)

	background.color = Color(
		0.015,
		0.020,
		0.035,
		0.94
	)

	background.mouse_filter = (
		Control.MOUSE_FILTER_STOP
	)

	add_child(
		background
	)

	var margin: MarginContainer = MarginContainer.new()

	margin.name = "InspectionMargin"

	margin.set_anchors_and_offsets_preset(
		Control.PRESET_FULL_RECT
	)

	margin.add_theme_constant_override(
		"margin_left",
		OUTER_MARGIN
	)

	margin.add_theme_constant_override(
		"margin_top",
		OUTER_MARGIN
	)

	margin.add_theme_constant_override(
		"margin_right",
		OUTER_MARGIN
	)

	margin.add_theme_constant_override(
		"margin_bottom",
		OUTER_MARGIN
	)

	add_child(
		margin
	)

	var panel: PanelContainer = _create_panel()

	panel.name = "InspectionPanel"

	margin.add_child(
		panel
	)

	var panel_margin: MarginContainer = MarginContainer.new()

	panel_margin.add_theme_constant_override(
		"margin_left",
		PANEL_PADDING
	)

	panel_margin.add_theme_constant_override(
		"margin_top",
		PANEL_PADDING
	)

	panel_margin.add_theme_constant_override(
		"margin_right",
		PANEL_PADDING
	)

	panel_margin.add_theme_constant_override(
		"margin_bottom",
		PANEL_PADDING
	)

	panel.add_child(
		panel_margin
	)

	var root: VBoxContainer = VBoxContainer.new()

	root.add_theme_constant_override(
		"separation",
		14
	)

	panel_margin.add_child(
		root
	)

	var header: HBoxContainer = HBoxContainer.new()

	root.add_child(
		header
	)

	var title: Label = Label.new()

	title.text = "DOCUMENT INSPECTION"

	title.add_theme_font_size_override(
		"font_size",
		26
	)

	title.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_PRIMARY
	)

	title.size_flags_horizontal = (
		Control.SIZE_EXPAND_FILL
	)

	header.add_child(
		title
	)

	var close_button: Button = Button.new()

	close_button.text = "CLOSE"

	close_button.custom_minimum_size = Vector2(
		100.0,
		42.0
	)

	close_button.pressed.connect(
		_close
	)

	header.add_child(
		close_button
	)

	var separator: HSeparator = HSeparator.new()

	root.add_child(
		separator
	)

	scroll_container = ScrollContainer.new()

	scroll_container.name = "InspectionScroll"

	scroll_container.horizontal_scroll_mode = (
		ScrollContainer.SCROLL_MODE_DISABLED
	)

	scroll_container.vertical_scroll_mode = (
		ScrollContainer.SCROLL_MODE_AUTO
	)

	scroll_container.size_flags_vertical = (
		Control.SIZE_EXPAND_FILL
	)

	root.add_child(
		scroll_container
	)

	var content: VBoxContainer = VBoxContainer.new()

	content.name = "InspectionContent"

	content.custom_minimum_size = Vector2(
		0.0,
		900.0
	)

	content.add_theme_constant_override(
		"separation",
		16
	)

	scroll_container.add_child(
		content
	)

	_build_identity_section(
		content
	)

	_build_metadata_section(
		content
	)

	_build_preprocessing_section(
		content
	)

	_build_chunks_section(
		content
	)

	_build_processing_section(
		content
	)

	_build_errors_section(
		content
	)

	_render_document()


func _build_identity_section(
	parent: VBoxContainer
) -> void:
	var panel: PanelContainer = _create_panel()

	panel.custom_minimum_size = Vector2(
		0.0,
		230.0
	)

	parent.add_child(
		panel
	)

	var content: VBoxContainer = _create_panel_content(
		panel
	)

	content.add_child(
		_create_heading(
			"DOCUMENT IDENTITY"
		)
	)

	identity_value = _create_value_label(
		"ID: —"
	)

	content.add_child(
		identity_value
	)

	title_value = _create_value_label(
		"Title: —"
	)

	content.add_child(
		title_value
	)

	source_value = _create_value_label(
		"Source: —"
	)

	content.add_child(
		source_value
	)

	type_value = _create_value_label(
		"Type: —"
	)

	content.add_child(
		type_value
	)

	state_value = _create_value_label(
		"Processing state: —"
	)

	content.add_child(
		state_value
	)


func _build_metadata_section(
	parent: VBoxContainer
) -> void:
	var panel: PanelContainer = _create_panel()

	panel.custom_minimum_size = Vector2(
		0.0,
		180.0
	)

	parent.add_child(
		panel
	)

	var content: VBoxContainer = _create_panel_content(
		panel
	)

	content.add_child(
		_create_heading(
			"METADATA"
		)
	)

	metadata_value = _create_value_label(
		"Metadata: —"
	)

	metadata_value.autowrap_mode = (
		TextServer.AUTOWRAP_WORD_SMART
	)

	content.add_child(
		metadata_value
	)


func _build_preprocessing_section(
	parent: VBoxContainer
) -> void:
	var panel: PanelContainer = _create_panel()

	panel.custom_minimum_size = Vector2(
		0.0,
		180.0
	)

	parent.add_child(
		panel
	)

	var content: VBoxContainer = _create_panel_content(
		panel
	)

	content.add_child(
		_create_heading(
			"PREPROCESSING"
		)
	)

	preprocessing_value = _create_value_label(
		"Preprocessing information: —"
	)

	preprocessing_value.autowrap_mode = (
		TextServer.AUTOWRAP_WORD_SMART
	)

	content.add_child(
		preprocessing_value
	)


func _build_chunks_section(
	parent: VBoxContainer
) -> void:
	var panel: PanelContainer = _create_panel()

	panel.custom_minimum_size = Vector2(
		0.0,
		420.0
	)

	parent.add_child(
		panel
	)

	var content: VBoxContainer = _create_panel_content(
		panel
	)

	content.add_child(
		_create_heading(
			"CHUNKS"
		)
	)

	var chunk_scroll: ScrollContainer = ScrollContainer.new()

	chunk_scroll.name = "ChunkScroll"

	chunk_scroll.custom_minimum_size = Vector2(
		0.0,
		330.0
	)

	chunk_scroll.horizontal_scroll_mode = (
		ScrollContainer.SCROLL_MODE_DISABLED
	)

	chunk_scroll.vertical_scroll_mode = (
		ScrollContainer.SCROLL_MODE_AUTO
	)

	content.add_child(
		chunk_scroll
	)

	chunks_container = VBoxContainer.new()

	chunks_container.name = "Chunks"

	chunks_container.add_theme_constant_override(
		"separation",
		8
	)

	chunk_scroll.add_child(
		chunks_container
	)


func _build_processing_section(
	parent: VBoxContainer
) -> void:
	var panel: PanelContainer = _create_panel()

	panel.custom_minimum_size = Vector2(
		0.0,
		200.0
	)

	parent.add_child(
		panel
	)

	var content: VBoxContainer = _create_panel_content(
		panel
	)

	content.add_child(
		_create_heading(
			"PROCESSING INFORMATION"
		)
	)

	processing_value = _create_value_label(
		"Processing information: —"
	)

	processing_value.autowrap_mode = (
		TextServer.AUTOWRAP_WORD_SMART
	)

	content.add_child(
		processing_value
	)


func _build_errors_section(
	parent: VBoxContainer
) -> void:
	var panel: PanelContainer = _create_panel()

	panel.custom_minimum_size = Vector2(
		0.0,
		200.0
	)

	parent.add_child(
		panel
	)

	var content: VBoxContainer = _create_panel_content(
		panel
	)

	content.add_child(
		_create_heading(
			"ERRORS"
		)
	)

	errors_value = _create_value_label(
		"No errors supplied."
	)

	errors_value.autowrap_mode = (
		TextServer.AUTOWRAP_WORD_SMART
	)

	content.add_child(
		errors_value
	)


func _render_document() -> void:
	if identity_value == null:
		return

	if document.is_empty():
		_render_empty_state()
		return

	var document_id: String = str(
		document.get(
			"id",
			"—"
		)
	)

	var title: String = str(
		document.get(
			"title",
			"—"
		)
	)

	var source: String = str(
		document.get(
			"source",
			document.get(
				"path",
				"—"
			)
		)
	)

	var document_type: String = str(
		document.get(
			"type",
			"—"
		)
	)

	var processing_state: String = str(
		document.get(
			"processing_state",
			"—"
		)
	)

	identity_value.text = (
		"ID: %s"
		% document_id
	)

	title_value.text = (
		"Title: %s"
		% title
	)

	source_value.text = (
		"Source: %s"
		% source
	)

	type_value.text = (
		"Type: %s"
		% document_type
	)

	state_value.text = (
		"Processing state: %s"
		% processing_state
	)

	_render_metadata()
	_render_preprocessing()
	_render_chunks()
	_render_processing()
	_render_errors()


func _render_empty_state() -> void:
	identity_value.text = "ID: —"
	title_value.text = "Title: —"
	source_value.text = "Source: —"
	type_value.text = "Type: —"
	state_value.text = "Processing state: —"

	metadata_value.text = (
		"Metadata: No document selected."
	)

	preprocessing_value.text = (
		"Preprocessing information: No document selected."
	)

	processing_value.text = (
		"Processing information: No document selected."
	)

	errors_value.text = (
		"No document selected."
	)

	for child in chunks_container.get_children():
		child.queue_free()

	var label: Label = _create_value_label(
		"No document selected."
	)

	chunks_container.add_child(
		label
	)


func _render_metadata() -> void:
	var metadata: Variant = document.get(
		"metadata",
		{}
	)

	if metadata is Dictionary:
		if metadata.is_empty():
			metadata_value.text = (
				"Metadata: —"
			)
		else:
			metadata_value.text = (
				"Metadata: %s"
				% JSON.stringify(
					metadata
				)
			)
	else:
		metadata_value.text = (
			"Metadata: %s"
			% str(metadata)
	)


func _render_preprocessing() -> void:
	var preprocessing: Variant = document.get(
		"preprocessing",
		document.get(
			"preprocessing_info",
			""
		)
	)

	if preprocessing is Dictionary:
		if preprocessing.is_empty():
			preprocessing_value.text = (
				"Preprocessing information: —"
			)
		else:
			preprocessing_value.text = (
				"Preprocessing information: %s"
				% JSON.stringify(
					preprocessing
				)
			)
	else:
		var text: String = str(
			preprocessing
		)

		if text.is_empty():
			text = "—"

		preprocessing_value.text = (
			"Preprocessing information: %s"
			% text
		)


func _render_chunks() -> void:
	for child in chunks_container.get_children():
		child.queue_free()

	var chunks: Variant = document.get(
		"chunks",
		[]
	)

	if not chunks is Array:
		chunks_container.add_child(
			_create_value_label(
				"No chunk data supplied."
			)
		)

		return

	if chunks.is_empty():
		chunks_container.add_child(
			_create_value_label(
				"No chunks supplied."
			)
		)

		return

	for index in chunks.size():
		var chunk_value: Variant = chunks[index]

		var chunk_panel: PanelContainer = _create_panel()

		chunk_panel.custom_minimum_size = Vector2(
			0.0,
			145.0
		)

		chunks_container.add_child(
			chunk_panel
		)

		var margin: MarginContainer = _create_panel_margin(
			chunk_panel
		)

		var content: VBoxContainer = VBoxContainer.new()

		content.add_theme_constant_override(
			"separation",
			6
		)

		margin.add_child(
			content
		)

		var chunk_title: Label = Label.new()

		chunk_title.text = (
			"CHUNK %d"
			% (index + 1)
		)

		chunk_title.add_theme_font_size_override(
			"font_size",
			14
		)

		chunk_title.add_theme_color_override(
			"font_color",
			StrontiumTokens.TEXT_PRIMARY
		)

		content.add_child(
			chunk_title
		)

		if chunk_value is Dictionary:
			_render_chunk_dictionary(
				content,
				chunk_value
			)
		else:
			var chunk_text: Label = _create_value_label(
				str(chunk_value)
			)

			chunk_text.autowrap_mode = (
				TextServer.AUTOWRAP_WORD_SMART
			)

			content.add_child(
				chunk_text
			)


func _render_chunk_dictionary(
	parent: VBoxContainer,
	chunk: Dictionary
) -> void:
	var start_value: String = str(
		chunk.get(
			"start",
			chunk.get(
				"start_index",
				"—"
			)
		)
	)

	var end_value: String = str(
		chunk.get(
			"end",
			chunk.get(
				"end_index",
				"—"
			)
		)
	)

	var text_value: String = str(
		chunk.get(
			"text",
			chunk.get(
				"content",
				""
			)
		)
	)

	var boundary_label: Label = _create_value_label(
		"Boundary: %s → %s"
		% [
			start_value,
			end_value
		]
	)

	parent.add_child(
		boundary_label
	)

	var text_label: Label = _create_value_label(
		"Content: %s"
		% (
			text_value
			if not text_value.is_empty()
			else "—"
		)
	)

	text_label.autowrap_mode = (
		TextServer.AUTOWRAP_WORD_SMART
	)

	parent.add_child(
		text_label
	)


func _render_processing() -> void:
	var processing: Variant = document.get(
		"processing",
		document.get(
			"processing_info",
			""
		)
	)

	if processing is Dictionary:
		if processing.is_empty():
			processing_value.text = (
				"Processing information: —"
			)
		else:
			processing_value.text = (
				"Processing information: %s"
				% JSON.stringify(
					processing
				)
			)
	else:
		var text: String = str(
			processing
		)

		if text.is_empty():
			text = "—"

		processing_value.text = (
			"Processing information: %s"
			% text
		)


func _render_errors() -> void:
	var errors: Variant = document.get(
		"errors",
		[]
	)

	if errors is Array:
		if errors.is_empty():
			errors_value.text = (
				"No errors supplied."
			)
		else:
			var lines: Array[String] = []

			for error_value in errors:
				lines.append(
					str(error_value)
				)

			errors_value.text = (
				"Errors:\n%s"
				% "\n".join(lines)
			)

	elif errors is Dictionary:
		if errors.is_empty():
			errors_value.text = (
				"No errors supplied."
			)
		else:
			errors_value.text = (
				"Errors: %s"
				% JSON.stringify(
					errors
				)
			)

	else:
		var error_text: String = str(
			errors
		)

		if error_text.is_empty():
			errors_value.text = (
				"No errors supplied."
			)
		else:
			errors_value.text = (
				"Errors: %s"
				% error_text
			)


func _create_panel() -> PanelContainer:
	var panel: PanelContainer = PanelContainer.new()

	var style: StyleBoxFlat = StyleBoxFlat.new()

	style.bg_color = Color(
		0.045,
		0.055,
		0.085,
		0.98
	)

	style.border_width_left = 1
	style.border_width_top = 1
	style.border_width_right = 1
	style.border_width_bottom = 1

	style.border_color = Color(
		0.15,
		0.18,
		0.24,
		0.90
	)

	style.corner_radius_top_left = 8
	style.corner_radius_top_right = 8
	style.corner_radius_bottom_left = 8
	style.corner_radius_bottom_right = 8

	panel.add_theme_stylebox_override(
		"panel",
		style
	)

	return panel


func _create_panel_content(
	panel: PanelContainer
) -> VBoxContainer:
	var margin: MarginContainer = _create_panel_margin(
		panel
	)

	var content: VBoxContainer = VBoxContainer.new()

	content.add_theme_constant_override(
		"separation",
		10
	)

	margin.add_child(
		content
	)

	return content


func _create_panel_margin(
	panel: PanelContainer
) -> MarginContainer:
	var margin: MarginContainer = MarginContainer.new()

	margin.add_theme_constant_override(
		"margin_left",
		PANEL_PADDING
	)

	margin.add_theme_constant_override(
		"margin_top",
		PANEL_PADDING
	)

	margin.add_theme_constant_override(
		"margin_right",
		PANEL_PADDING
	)

	margin.add_theme_constant_override(
		"margin_bottom",
		PANEL_PADDING
	)

	panel.add_child(
		margin
	)

	return margin


func _create_heading(
	text_value: String
) -> Label:
	var heading: Label = Label.new()

	heading.text = text_value

	heading.add_theme_font_size_override(
		"font_size",
		17
	)

	heading.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_PRIMARY
	)

	return heading


func _create_value_label(
	text_value: String
) -> Label:
	var label: Label = Label.new()

	label.text = text_value

	label.add_theme_font_size_override(
		"font_size",
		14
	)

	label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	label.autowrap_mode = (
		TextServer.AUTOWRAP_WORD_SMART
	)

	return label


func _close() -> void:
	closed.emit()

	queue_free()
