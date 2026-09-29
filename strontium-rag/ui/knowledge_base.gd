class_name StrontiumKnowledgeBase
extends Control


signal document_selected(document: Dictionary)
signal search_changed(query: String)
signal refresh_requested()


const CONTENT_MARGIN: int = 32
const PANEL_PADDING: int = 24

const STATE_EMPTY: String = "EMPTY"
const STATE_READY: String = "READY"
const STATE_LOADING: String = "LOADING"
const STATE_ERROR: String = "ERROR"


var workflow_state: String = STATE_EMPTY

var documents: Array[Dictionary] = []
var filtered_documents: Array[Dictionary] = []

var selected_document: Dictionary = {}
var selected_document_index: int = -1

var search_query: String = ""

var document_detail: StrontiumDocumentDetail = null


var search_field: LineEdit = null
var document_list: VBoxContainer = null
var document_count_label: Label = null
var status_label: Label = null

var selected_title_label: Label = null
var selected_source_label: Label = null
var selected_metadata_label: Label = null
var selected_chunks_label: Label = null
var selected_state_label: Label = null
var selected_details_label: Label = null

var refresh_button: Button = null
var clear_search_button: Button = null

var stat_documents_value: Label = null
var stat_chunks_value: Label = null
var stat_sources_value: Label = null


func _ready() -> void:
	set_anchors_and_offsets_preset(
		Control.PRESET_FULL_RECT
	)

	mouse_filter = Control.MOUSE_FILTER_PASS

	_build_interface()

	_set_state(
		STATE_EMPTY
	)


func _build_interface() -> void:
	for child in get_children():
		child.queue_free()

	var margin: MarginContainer = MarginContainer.new()

	margin.name = "KnowledgeBaseMargin"

	margin.set_anchors_and_offsets_preset(
		Control.PRESET_FULL_RECT
	)

	margin.add_theme_constant_override(
		"margin_left",
		CONTENT_MARGIN
	)

	margin.add_theme_constant_override(
		"margin_top",
		CONTENT_MARGIN
	)

	margin.add_theme_constant_override(
		"margin_right",
		CONTENT_MARGIN
	)

	margin.add_theme_constant_override(
		"margin_bottom",
		CONTENT_MARGIN
	)

	add_child(
		margin
	)

	var scroll: ScrollContainer = ScrollContainer.new()

	scroll.name = "KnowledgeBaseScroll"

	scroll.horizontal_scroll_mode = (
		ScrollContainer.SCROLL_MODE_DISABLED
	)

	scroll.vertical_scroll_mode = (
		ScrollContainer.SCROLL_MODE_AUTO
	)

	scroll.size_flags_horizontal = (
		Control.SIZE_EXPAND_FILL
	)

	scroll.size_flags_vertical = (
		Control.SIZE_EXPAND_FILL
	)

	margin.add_child(
		scroll
	)

	var content: VBoxContainer = VBoxContainer.new()

	content.name = "KnowledgeBaseContent"

	content.custom_minimum_size = Vector2(
		0.0,
		1150.0
	)

	content.add_theme_constant_override(
		"separation",
		18
	)

	scroll.add_child(
		content
	)

	_build_header(
		content
	)

	_build_statistics(
		content
	)

	_build_search(
		content
	)

	_build_documents_panel(
		content
	)

	_build_details_panel(
		content
	)


func _build_header(
	parent: VBoxContainer
) -> void:
	var title: Label = Label.new()

	title.text = "KNOWLEDGE BASE"

	title.add_theme_font_size_override(
		"font_size",
		30
	)

	title.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_PRIMARY
	)

	title.mouse_filter = (
		Control.MOUSE_FILTER_IGNORE
	)

	parent.add_child(
		title
	)

	var subtitle: Label = Label.new()

	subtitle.text = "Explore documents, sources, metadata, processing state, and stored RAG knowledge."

	subtitle.add_theme_font_size_override(
		"font_size",
		15
	)

	subtitle.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	subtitle.autowrap_mode = (
		TextServer.AUTOWRAP_WORD_SMART
	)

	subtitle.mouse_filter = (
		Control.MOUSE_FILTER_IGNORE
	)

	parent.add_child(
		subtitle
	)


func _build_statistics(
	parent: VBoxContainer
) -> void:
	var panel: PanelContainer = _create_panel()

	panel.name = "KnowledgeBaseStatistics"

	panel.custom_minimum_size = Vector2(
		0.0,
		150.0
	)

	parent.add_child(
		panel
	)

	var margin: MarginContainer = _create_panel_margin(
		panel
	)

	var row: HBoxContainer = HBoxContainer.new()

	row.add_theme_constant_override(
		"separation",
		18
	)

	margin.add_child(
		row
	)

	stat_documents_value = _create_metric(
		row,
		"DOCUMENTS"
	)

	stat_chunks_value = _create_metric(
		row,
		"CHUNKS"
	)

	stat_sources_value = _create_metric(
		row,
		"SOURCES"
	)


func _create_metric(
	parent: HBoxContainer,
	title: String
) -> Label:
	var panel: PanelContainer = _create_panel()

	panel.custom_minimum_size = Vector2(
		0.0,
		90.0
	)

	panel.size_flags_horizontal = (
		Control.SIZE_EXPAND_FILL
	)

	parent.add_child(
		panel
	)

	var margin: MarginContainer = _create_panel_margin(
		panel
	)

	var content: VBoxContainer = VBoxContainer.new()

	content.add_theme_constant_override(
		"separation",
		4
	)

	margin.add_child(
		content
	)

	var title_label: Label = Label.new()

	title_label.text = title

	title_label.add_theme_font_size_override(
		"font_size",
		11
	)

	title_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	content.add_child(
		title_label
	)

	var value: Label = Label.new()

	value.text = "—"

	value.add_theme_font_size_override(
		"font_size",
		24
	)

	value.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_PRIMARY
	)

	content.add_child(
		value
	)

	return value


func _build_search(
	parent: VBoxContainer
) -> void:
	var panel: PanelContainer = _create_panel()

	panel.name = "KnowledgeBaseSearch"

	panel.custom_minimum_size = Vector2(
		0.0,
		105.0
	)

	parent.add_child(
		panel
	)

	var margin: MarginContainer = _create_panel_margin(
		panel
	)

	var row: HBoxContainer = HBoxContainer.new()

	row.add_theme_constant_override(
		"separation",
		12
	)

	margin.add_child(
		row
	)

	search_field = LineEdit.new()

	search_field.name = "SearchDocuments"

	search_field.placeholder_text = "Search documents..."

	search_field.custom_minimum_size = Vector2(
		0.0,
		46.0
	)

	search_field.size_flags_horizontal = (
		Control.SIZE_EXPAND_FILL
	)

	search_field.text_changed.connect(
		_on_search_changed
	)

	row.add_child(
		search_field
	)

	clear_search_button = Button.new()

	clear_search_button.text = "CLEAR"

	clear_search_button.custom_minimum_size = Vector2(
		100.0,
		46.0
	)

	clear_search_button.pressed.connect(
		_clear_search
	)

	row.add_child(
		clear_search_button
	)

	refresh_button = Button.new()

	refresh_button.text = "REFRESH"

	refresh_button.custom_minimum_size = Vector2(
		110.0,
		46.0
	)

	refresh_button.pressed.connect(
		_on_refresh_pressed
	)

	row.add_child(
		refresh_button
	)


func _build_documents_panel(
	parent: VBoxContainer
) -> void:
	var panel: PanelContainer = _create_panel()

	panel.name = "DocumentsPanel"

	panel.custom_minimum_size = Vector2(
		0.0,
		380.0
	)

	parent.add_child(
		panel
	)

	var margin: MarginContainer = _create_panel_margin(
		panel
	)

	var content: VBoxContainer = VBoxContainer.new()

	content.add_theme_constant_override(
		"separation",
		12
	)

	margin.add_child(
		content
	)

	var header: HBoxContainer = HBoxContainer.new()

	content.add_child(
		header
	)

	var heading: Label = _create_heading(
		"DOCUMENTS"
	)

	header.add_child(
		heading
	)

	document_count_label = Label.new()

	document_count_label.text = "0 documents"

	document_count_label.size_flags_horizontal = (
		Control.SIZE_EXPAND_FILL
	)

	document_count_label.horizontal_alignment = (
		HORIZONTAL_ALIGNMENT_RIGHT
	)

	document_count_label.add_theme_font_size_override(
		"font_size",
		13
	)

	document_count_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	header.add_child(
		document_count_label
	)

	status_label = Label.new()

	status_label.text = "Knowledge base data is not connected."

	status_label.add_theme_font_size_override(
		"font_size",
		13
	)

	status_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	status_label.autowrap_mode = (
		TextServer.AUTOWRAP_WORD_SMART
	)

	content.add_child(
		status_label
	)

	var list_scroll: ScrollContainer = ScrollContainer.new()

	list_scroll.name = "DocumentListScroll"

	list_scroll.custom_minimum_size = Vector2(
		0.0,
		250.0
	)

	list_scroll.horizontal_scroll_mode = (
		ScrollContainer.SCROLL_MODE_DISABLED
	)

	list_scroll.vertical_scroll_mode = (
		ScrollContainer.SCROLL_MODE_AUTO
	)

	content.add_child(
		list_scroll
	)

	document_list = VBoxContainer.new()

	document_list.name = "DocumentList"

	document_list.add_theme_constant_override(
		"separation",
		8
	)

	document_list.size_flags_horizontal = (
		Control.SIZE_EXPAND_FILL
	)

	list_scroll.add_child(
		document_list
	)


func _build_details_panel(
	parent: VBoxContainer
) -> void:
	var panel: PanelContainer = _create_panel()

	panel.name = "DocumentDetailsPanel"

	panel.custom_minimum_size = Vector2(
		0.0,
		360.0
	)

	parent.add_child(
		panel
	)

	var margin: MarginContainer = _create_panel_margin(
		panel
	)

	var content: VBoxContainer = VBoxContainer.new()

	content.add_theme_constant_override(
		"separation",
		12
	)

	margin.add_child(
		content
	)

	content.add_child(
		_create_heading(
			"DOCUMENT DETAILS"
		)
	)

	selected_title_label = _create_detail_label(
		"NO DOCUMENT SELECTED"
	)

	selected_title_label.add_theme_font_size_override(
		"font_size",
		22
	)

	selected_title_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_PRIMARY
	)

	content.add_child(
		selected_title_label
	)

	selected_source_label = _create_detail_label(
		"Source: —"
	)

	content.add_child(
		selected_source_label
	)

	selected_metadata_label = _create_detail_label(
		"Metadata: —"
	)

	selected_metadata_label.autowrap_mode = (
		TextServer.AUTOWRAP_WORD_SMART
	)

	content.add_child(
		selected_metadata_label
	)

	selected_chunks_label = _create_detail_label(
		"Chunks: —"
	)

	content.add_child(
		selected_chunks_label
	)

	selected_state_label = _create_detail_label(
		"Processing state: —"
	)

	content.add_child(
		selected_state_label
	)

	selected_details_label = _create_detail_label(
		"Select a document to inspect its complete structure."
	)

	selected_details_label.autowrap_mode = (
		TextServer.AUTOWRAP_WORD_SMART
	)

	content.add_child(
		selected_details_label
	)


func _create_detail_label(
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

	return label


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

	heading.mouse_filter = (
		Control.MOUSE_FILTER_IGNORE
	)

	return heading


func _create_panel() -> PanelContainer:
	var panel: PanelContainer = PanelContainer.new()

	var style: StyleBoxFlat = StyleBoxFlat.new()

	style.bg_color = Color(
		0.045,
		0.055,
		0.085,
		0.96
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


func _on_search_changed(
	query: String
) -> void:
	search_query = query.strip_edges()

	search_changed.emit(
		search_query
	)

	_apply_filter()


func _clear_search() -> void:
	search_field.text = ""


func _on_refresh_pressed() -> void:
	refresh_requested.emit()


func _apply_filter() -> void:
	filtered_documents.clear()

	if search_query.is_empty():
		filtered_documents = documents.duplicate(
			true
		)
	else:
		var normalized_query: String = (
			search_query.to_lower()
		)

		for document in documents:
			if _document_matches(
				document,
				normalized_query
			):
				filtered_documents.append(
					document
				)

	_render_document_list()


func _document_matches(
	document: Dictionary,
	query: String
) -> bool:
	var searchable_values: Array[String] = [
		str(document.get("id", "")),
		str(document.get("title", "")),
		str(document.get("source", "")),
		str(document.get("path", "")),
		str(document.get("type", "")),
		str(document.get("processing_state", ""))
	]

	for value in searchable_values:
		if value.to_lower().contains(query):
			return true

	var metadata_value: Variant = (
		document.get(
			"metadata",
			{}
		)
	)

	if metadata_value is Dictionary:
		for metadata_key in metadata_value.keys():
			var metadata_text: String = (
				str(metadata_key)
				+ " "
				+ str(metadata_value[metadata_key])
			)

			if metadata_text.to_lower().contains(
				query
			):
				return true

	return false


func _render_document_list() -> void:
	if document_list == null:
		return

	for child in document_list.get_children():
		child.queue_free()

	document_count_label.text = (
		"%d document(s)"
		% filtered_documents.size()
	)

	if filtered_documents.is_empty():
		var empty_label: Label = Label.new()

		if documents.is_empty():
			empty_label.text = "No documents are currently available from the knowledge base."
		else:
			empty_label.text = "No documents match the current search."

		empty_label.add_theme_font_size_override(
			"font_size",
			14
		)

		empty_label.add_theme_color_override(
			"font_color",
			StrontiumTokens.TEXT_SECONDARY
		)

		empty_label.autowrap_mode = (
			TextServer.AUTOWRAP_WORD_SMART
		)

		document_list.add_child(
			empty_label
		)

		return

	for index in filtered_documents.size():
		var document: Dictionary = (
			filtered_documents[index]
		)

		var row: Button = _create_document_row(
			document,
			index
		)

		document_list.add_child(
			row
		)


func _create_document_row(
	document: Dictionary,
	index: int
) -> Button:
	var button: Button = Button.new()

	button.name = (
		"DocumentRow_%d" % index
	)

	button.alignment = (
		HORIZONTAL_ALIGNMENT_LEFT
	)

	button.custom_minimum_size = Vector2(
		0.0,
		82.0
	)

	var title: String = str(
		document.get(
			"title",
			document.get(
				"source",
				document.get(
					"id",
					"Untitled document"
				)
			)
		)
	)

	var source: String = str(
		document.get(
			"source",
			"Unknown source"
		)
	)

	var chunks: String = str(
		document.get(
			"chunk_count",
			"—"
		)
	)

	var processing_state: String = str(
		document.get(
			"processing_state",
			"UNKNOWN"
		)
	)

	button.text = (
		"%s\n%s  •  %s chunks  •  %s"
		% [
			title,
			source,
			chunks,
			processing_state
		]
	)

	button.add_theme_font_size_override(
		"font_size",
		14
	)

	button.pressed.connect(
		_select_document.bind(
			document
		)
	)

	return button


func _select_document(
	document: Dictionary
) -> void:
	selected_document = document.duplicate(
		true
	)

	var source: String = str(
		selected_document.get(
			"source",
			selected_document.get(
				"path",
				"—"
			)
		)
	)

	var title: String = str(
		selected_document.get(
			"title",
			source
		)
	)

	var chunks: String = str(
		selected_document.get(
			"chunk_count",
			"—"
		)
	)

	var processing_state: String = str(
		selected_document.get(
			"processing_state",
			"UNKNOWN"
		)
	)

	var metadata: Variant = (
		selected_document.get(
			"metadata",
			{}
		)
	)

	selected_title_label.text = title

	selected_source_label.text = (
		"Source: %s"
		% source
	)

	selected_chunks_label.text = (
		"Chunks: %s"
		% chunks
	)

	selected_state_label.text = (
		"Processing state: %s"
		% processing_state
	)

	if metadata is Dictionary:
		if metadata.is_empty():
			selected_metadata_label.text = (
				"Metadata: —"
			)
		else:
			selected_metadata_label.text = (
				"Metadata: %s"
				% JSON.stringify(
					metadata
				)
			)
	else:
		selected_metadata_label.text = (
			"Metadata: %s"
			% str(metadata)
	)

	selected_details_label.text = "Select DOCUMENT INSPECTION to examine identity, preprocessing, chunks, boundaries, processing information, and errors."

	_show_document_detail()

	document_selected.emit(
		selected_document
	)


func _show_document_detail() -> void:
	if document_detail != null:
		if is_instance_valid(document_detail):
			document_detail.queue_free()

	document_detail = StrontiumDocumentDetail.new()

	document_detail.name = "DocumentDetail"

	document_detail.set_anchors_and_offsets_preset(
		Control.PRESET_FULL_RECT
	)

	document_detail.closed.connect(
		_on_document_detail_closed
	)

	add_child(
		document_detail
	)

	document_detail.set_document(
		selected_document
	)


func _on_document_detail_closed() -> void:
	document_detail = null


func _set_state(
	new_state: String
) -> void:
	workflow_state = new_state

	if status_label == null:
		return

	match new_state:
		STATE_EMPTY:
			status_label.text = "Knowledge base data is not connected."

		STATE_READY:
			status_label.text = "Knowledge base data is available."

		STATE_LOADING:
			status_label.text = "Loading knowledge base data."

		STATE_ERROR:
			status_label.text = "Knowledge base data could not be loaded."


func set_documents(
	new_documents: Array
) -> void:
	documents.clear()

	for item in new_documents:
		if item is Dictionary:
			documents.append(
				item.duplicate(
					true
				)
			)

	_update_statistics()

	_apply_filter()

	if documents.is_empty():
		_set_state(
			STATE_EMPTY
		)
	else:
		_set_state(
			STATE_READY
		)


func set_loading() -> void:
	_set_state(
		STATE_LOADING
	)


func set_error(
	detail: String
) -> void:
	_set_state(
		STATE_ERROR
	)

	status_label.text = detail


func clear_documents() -> void:
	documents.clear()
	filtered_documents.clear()
	selected_document.clear()
	selected_document_index = -1

	_update_statistics()
	_render_document_list()

	_set_state(
		STATE_EMPTY
	)


func get_documents() -> Array[Dictionary]:
	return documents.duplicate(
		true
	)


func get_filtered_documents() -> Array[Dictionary]:
	return filtered_documents.duplicate(
		true
	)


func get_selected_document() -> Dictionary:
	return selected_document.duplicate(
		true
	)


func get_state() -> String:
	return workflow_state


func _update_statistics() -> void:
	if stat_documents_value == null:
		return

	stat_documents_value.text = str(
		documents.size()
	)

	var total_chunks: int = 0
	var sources: Dictionary = {}

	for document in documents:
		var chunk_value: Variant = (
			document.get(
				"chunk_count",
				0
			)
		)

		if chunk_value is int:
			total_chunks += chunk_value
		elif chunk_value is float:
			total_chunks += int(
				chunk_value
			)

		var source: String = str(
			document.get(
				"source",
				document.get(
					"path",
					""
				)
			)
		)

		if not source.is_empty():
			sources[source] = true

	stat_chunks_value.text = str(
		total_chunks
	)

	stat_sources_value.text = str(
		sources.size()
	)
