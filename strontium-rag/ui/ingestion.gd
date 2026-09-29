class_name StrontiumIngestion
extends Control


signal ingestion_requested(payload: Dictionary)
signal ingestion_cancelled()
signal workflow_state_changed(state: String)


const STATE_READY: String = "READY"
const STATE_REQUEST_READY: String = "REQUEST READY"
const STATE_WAITING_BACKEND: String = "WAITING FOR BACKEND"
const STATE_PROCESSING: String = "PROCESSING"
const STATE_SUCCESS: String = "SUCCESS"
const STATE_FAILURE: String = "FAILURE"


const SOURCE_FILES: String = "FILES"
const SOURCE_DIRECTORY: String = "DIRECTORY"


const CONTENT_MARGIN: int = 32
const CARD_PADDING: int = 24


var source_mode: String = SOURCE_FILES
var selected_files: Array[String] = []
var selected_directory: String = ""

var workflow_state: String = STATE_READY
var processing_progress: float = 0.0

var source_path_field: LineEdit = null
var source_status_label: Label = null
var backend_status_label: Label = null

var workflow_state_label: Label = null
var workflow_detail_label: Label = null
var progress_bar: ProgressBar = null

var recursive_check: CheckBox = null
var include_hidden_check: CheckBox = null

var selected_targets_value: Label = null
var processed_documents_value: Label = null
var chunks_created_value: Label = null
var failures_value: Label = null

var prepare_button: Button = null
var clear_button: Button = null

var file_dialog: FileDialog = null


func _ready() -> void:
	set_anchors_and_offsets_preset(
		Control.PRESET_FULL_RECT
	)

	mouse_filter = Control.MOUSE_FILTER_PASS

	_build_interface()
	_set_state(STATE_READY)


func _build_interface() -> void:
	for child in get_children():
		child.queue_free()

	var margin: MarginContainer = MarginContainer.new()
	margin.name = "IngestionMargin"

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

	add_child(margin)

	var scroll: ScrollContainer = ScrollContainer.new()
	scroll.name = "IngestionScroll"

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

	margin.add_child(scroll)

	var content: VBoxContainer = VBoxContainer.new()
	content.name = "IngestionContent"

	content.custom_minimum_size = Vector2(
		0.0,
		1050.0
	)

	content.add_theme_constant_override(
		"separation",
		18
	)

	scroll.add_child(content)

	_build_header(content)
	_build_backend_status(content)
	_build_source_section(content)
	_build_options_section(content)
	_build_processing_section(content)
	_build_statistics_section(content)


func _build_header(
	parent: VBoxContainer
) -> void:
	var title: Label = Label.new()

	title.text = "DOCUMENT INGESTION"

	title.add_theme_font_size_override(
		"font_size",
		30
	)

	title.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_PRIMARY
	)

	title.mouse_filter = Control.MOUSE_FILTER_IGNORE

	parent.add_child(title)

	var subtitle: Label = Label.new()

	subtitle.text = "Prepare documents for ingestion into the Strontium knowledge base."

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

	subtitle.mouse_filter = Control.MOUSE_FILTER_IGNORE

	parent.add_child(subtitle)


func _build_backend_status(
	parent: VBoxContainer
) -> void:
	var panel: PanelContainer = _create_panel()
	panel.name = "BackendStatusPanel"

	panel.custom_minimum_size = Vector2(
		0.0,
		105.0
	)

	parent.add_child(panel)

	var content: VBoxContainer = _create_panel_content(
		panel
	)

	var heading: Label = _create_heading(
		"INGESTION ENGINE"
	)

	content.add_child(heading)

	backend_status_label = Label.new()

	backend_status_label.text = "APPLICATION LAYER ACTIVE — Python ingestion integration is not connected."

	backend_status_label.add_theme_font_size_override(
		"font_size",
		14
	)

	backend_status_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	backend_status_label.autowrap_mode = (
		TextServer.AUTOWRAP_WORD_SMART
	)

	content.add_child(
		backend_status_label
	)


func _build_source_section(
	parent: VBoxContainer
) -> void:
	var panel: PanelContainer = _create_panel()
	panel.name = "SourceSelectionPanel"

	panel.custom_minimum_size = Vector2(
		0.0,
		245.0
	)

	parent.add_child(panel)

	var content: VBoxContainer = _create_panel_content(
		panel
	)

	content.add_child(
		_create_heading("SOURCE")
	)

	source_status_label = Label.new()

	source_status_label.text = "Choose documents or a directory."

	source_status_label.add_theme_font_size_override(
		"font_size",
		14
	)

	source_status_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	source_status_label.autowrap_mode = (
		TextServer.AUTOWRAP_WORD_SMART
	)

	content.add_child(
		source_status_label
	)

	source_path_field = LineEdit.new()

	source_path_field.name = "SourcePath"

	source_path_field.editable = false

	source_path_field.placeholder_text = "No source selected"

	source_path_field.custom_minimum_size = Vector2(
		0.0,
		44.0
	)

	content.add_child(
		source_path_field
	)

	var button_row: HBoxContainer = HBoxContainer.new()

	button_row.add_theme_constant_override(
		"separation",
		12
	)

	content.add_child(
		button_row
	)

	var file_button: Button = Button.new()

	file_button.text = "SELECT FILES"

	file_button.custom_minimum_size = Vector2(
		150.0,
		44.0
	)

	file_button.pressed.connect(
		_open_file_dialog
	)

	button_row.add_child(
		file_button
	)

	var directory_button: Button = Button.new()

	directory_button.text = "SELECT DIRECTORY"

	directory_button.custom_minimum_size = Vector2(
		175.0,
		44.0
	)

	directory_button.pressed.connect(
		_open_directory_dialog
	)

	button_row.add_child(
		directory_button
	)

	clear_button = Button.new()

	clear_button.text = "CLEAR"

	clear_button.custom_minimum_size = Vector2(
		100.0,
		44.0
	)

	clear_button.pressed.connect(
		_clear_source
	)

	button_row.add_child(
		clear_button
	)


func _build_options_section(
	parent: VBoxContainer
) -> void:
	var panel: PanelContainer = _create_panel()
	panel.name = "IngestionOptionsPanel"

	panel.custom_minimum_size = Vector2(
		0.0,
		205.0
	)

	parent.add_child(panel)

	var content: VBoxContainer = _create_panel_content(
		panel
	)

	content.add_child(
		_create_heading("INGESTION OPTIONS")
	)

	recursive_check = CheckBox.new()

	recursive_check.text = "Process subdirectories recursively"

	recursive_check.button_pressed = true

	content.add_child(
		recursive_check
	)

	include_hidden_check = CheckBox.new()

	include_hidden_check.text = "Include hidden files"

	include_hidden_check.button_pressed = false

	content.add_child(
		include_hidden_check
	)

	prepare_button = Button.new()

	prepare_button.text = "PREPARE INGESTION REQUEST"

	prepare_button.custom_minimum_size = Vector2(
		0.0,
		48.0
	)

	prepare_button.pressed.connect(
		_prepare_ingestion
	)

	content.add_child(
		prepare_button
	)


func _build_processing_section(
	parent: VBoxContainer
) -> void:
	var panel: PanelContainer = _create_panel()
	panel.name = "ProcessingPanel"

	panel.custom_minimum_size = Vector2(
		0.0,
		260.0
	)

	parent.add_child(panel)

	var content: VBoxContainer = _create_panel_content(
		panel
	)

	content.add_child(
		_create_heading("PROCESSING STATE")
	)

	workflow_state_label = Label.new()

	workflow_state_label.text = STATE_READY

	workflow_state_label.add_theme_font_size_override(
		"font_size",
		21
	)

	workflow_state_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_PRIMARY
	)

	content.add_child(
		workflow_state_label
	)

	workflow_detail_label = Label.new()

	workflow_detail_label.text = "Waiting for a source."

	workflow_detail_label.add_theme_font_size_override(
		"font_size",
		14
	)

	workflow_detail_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	workflow_detail_label.autowrap_mode = (
		TextServer.AUTOWRAP_WORD_SMART
	)

	content.add_child(
		workflow_detail_label
	)

	progress_bar = ProgressBar.new()

	progress_bar.name = "ProcessingProgress"

	progress_bar.min_value = 0.0
	progress_bar.max_value = 100.0
	progress_bar.value = 0.0
	progress_bar.show_percentage = true

	progress_bar.custom_minimum_size = Vector2(
		0.0,
		30.0
	)

	content.add_child(
		progress_bar
	)


func _build_statistics_section(
	parent: VBoxContainer
) -> void:
	var panel: PanelContainer = _create_panel()
	panel.name = "StatisticsPanel"

	panel.custom_minimum_size = Vector2(
		0.0,
		245.0
	)

	parent.add_child(panel)

	var content: VBoxContainer = _create_panel_content(
		panel
	)

	content.add_child(
		_create_heading("INGESTION STATISTICS")
	)

	selected_targets_value = _add_stat_row(
		content,
		"Selected targets"
	)

	processed_documents_value = _add_stat_row(
		content,
		"Documents processed"
	)

	chunks_created_value = _add_stat_row(
		content,
		"Chunks created"
	)

	failures_value = _add_stat_row(
		content,
		"Failures"
	)


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


func _create_panel_content(
	panel: PanelContainer
) -> VBoxContainer:
	var margin: MarginContainer = MarginContainer.new()

	margin.add_theme_constant_override(
		"margin_left",
		CARD_PADDING
	)

	margin.add_theme_constant_override(
		"margin_top",
		CARD_PADDING
	)

	margin.add_theme_constant_override(
		"margin_right",
		CARD_PADDING
	)

	margin.add_theme_constant_override(
		"margin_bottom",
		CARD_PADDING
	)

	panel.add_child(
		margin
	)

	var content: VBoxContainer = VBoxContainer.new()

	content.add_theme_constant_override(
		"separation",
		12
	)

	margin.add_child(
		content
	)

	return content


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


func _add_stat_row(
	parent: VBoxContainer,
	label_text: String
) -> Label:
	var row: HBoxContainer = HBoxContainer.new()

	var label: Label = Label.new()

	label.text = label_text

	label.size_flags_horizontal = (
		Control.SIZE_EXPAND_FILL
	)

	label.add_theme_font_size_override(
		"font_size",
		14
	)

	label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	var value: Label = Label.new()

	value.text = "—"

	value.horizontal_alignment = (
		HORIZONTAL_ALIGNMENT_RIGHT
	)

	value.add_theme_font_size_override(
		"font_size",
		14
	)

	value.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_PRIMARY
	)

	row.add_child(label)
	row.add_child(value)

	parent.add_child(row)

	return value


func _open_file_dialog() -> void:
	_close_file_dialog()

	file_dialog = FileDialog.new()

	file_dialog.name = "IngestionFileDialog"

	file_dialog.file_mode = (
		FileDialog.FILE_MODE_OPEN_FILES
	)

	file_dialog.access = (
		FileDialog.ACCESS_FILESYSTEM
	)

	file_dialog.title = "Select Documents"

	file_dialog.size = Vector2i(
		900,
		600
	)

	file_dialog.files_selected.connect(
		_on_files_selected
	)

	add_child(file_dialog)

	file_dialog.popup_centered()


func _open_directory_dialog() -> void:
	_close_file_dialog()

	file_dialog = FileDialog.new()

	file_dialog.name = "IngestionDirectoryDialog"

	file_dialog.file_mode = (
		FileDialog.FILE_MODE_OPEN_DIR
	)

	file_dialog.access = (
		FileDialog.ACCESS_FILESYSTEM
	)

	file_dialog.title = "Select Document Directory"

	file_dialog.size = Vector2i(
		900,
		600
	)

	file_dialog.dir_selected.connect(
		_on_directory_selected
	)

	add_child(file_dialog)

	file_dialog.popup_centered()


func _close_file_dialog() -> void:
	if file_dialog == null:
		return

	if is_instance_valid(file_dialog):
		file_dialog.queue_free()

	file_dialog = null


func _on_files_selected(
	paths: PackedStringArray
) -> void:
	selected_files.clear()
	selected_directory = ""

	for path in paths:
		if not str(path).is_empty():
			selected_files.append(
				str(path)
			)

	source_mode = SOURCE_FILES

	if selected_files.is_empty():
		source_path_field.text = ""
		source_status_label.text = "No files selected."
	else:
		source_path_field.text = (
			"%d file(s) selected"
			% selected_files.size()
		)

		source_status_label.text = (
			"%d document(s) selected."
			% selected_files.size()
		)

	_update_source_statistics()

	_set_state(
		STATE_READY
	)


func _on_directory_selected(
	path: String
) -> void:
	selected_files.clear()

	selected_directory = path

	source_mode = SOURCE_DIRECTORY

	source_path_field.text = path

	source_status_label.text = (
		"Directory selected. Recursive processing: %s."
		% (
			"enabled"
			if recursive_check.button_pressed
			else "disabled"
		)
	)

	_update_source_statistics()

	_set_state(
		STATE_READY
	)


func _clear_source() -> void:
	selected_files.clear()
	selected_directory = ""

	source_path_field.text = ""

	source_status_label.text = (
		"Choose documents or a directory."
	)

	_reset_statistics()

	progress_bar.value = 0.0

	processing_progress = 0.0

	_set_state(
		STATE_READY
	)

	ingestion_cancelled.emit()


func _prepare_ingestion() -> void:
	if not _has_source():
		set_failure(
			"No documents or directory have been selected."
		)

		return

	var payload: Dictionary = (
		_build_ingestion_payload()
	)

	ingestion_requested.emit(
		payload
	)

	_set_state(
		STATE_WAITING_BACKEND,
		"Request prepared and emitted. No documents have been processed because the Python ingestion backend is not connected."
	)


func _has_source() -> bool:
	if source_mode == SOURCE_FILES:
		return not selected_files.is_empty()

	if source_mode == SOURCE_DIRECTORY:
		return not selected_directory.is_empty()

	return false


func _build_ingestion_payload() -> Dictionary:
	return {
		"operation": "document_ingestion",
		"source_mode": source_mode,
		"files": selected_files.duplicate(),
		"directory": selected_directory,
		"options": {
			"recursive": recursive_check.button_pressed,
			"include_hidden": include_hidden_check.button_pressed
		}
	}


func _update_source_statistics() -> void:
	var count: int = 0

	if source_mode == SOURCE_FILES:
		count = selected_files.size()

	elif source_mode == SOURCE_DIRECTORY:
		count = 1

	selected_targets_value.text = str(count)

	processed_documents_value.text = "—"
	chunks_created_value.text = "—"
	failures_value.text = "—"


func _reset_statistics() -> void:
	selected_targets_value.text = "—"
	processed_documents_value.text = "—"
	chunks_created_value.text = "—"
	failures_value.text = "—"


func _set_state(
	new_state: String,
	detail: String = ""
) -> void:
	workflow_state = new_state

	workflow_state_label.text = new_state

	if detail.is_empty():
		match new_state:
			STATE_READY:
				workflow_detail_label.text = "Waiting for a source."

			STATE_REQUEST_READY:
				workflow_detail_label.text = "Ingestion request is ready."

			STATE_WAITING_BACKEND:
				workflow_detail_label.text = "Waiting for Python integration."

			STATE_PROCESSING:
				workflow_detail_label.text = "Ingestion is currently processing."

			STATE_SUCCESS:
				workflow_detail_label.text = "Ingestion completed."

			STATE_FAILURE:
				workflow_detail_label.text = "Ingestion could not continue."
	else:
		workflow_detail_label.text = detail

	workflow_state_changed.emit(
		new_state
	)


func set_processing(
	progress: float,
	detail: String = ""
) -> void:
	processing_progress = clampf(
		progress,
		0.0,
		100.0
	)

	progress_bar.value = processing_progress

	_set_state(
		STATE_PROCESSING,
		detail
	)


func set_success(
	processed_documents: int,
	chunks_created: int,
	failures: int = 0,
	detail: String = ""
) -> void:
	processed_documents_value.text = str(
		processed_documents
	)

	chunks_created_value.text = str(
		chunks_created
	)

	failures_value.text = str(
		failures
	)

	processing_progress = 100.0

	progress_bar.value = 100.0

	_set_state(
		STATE_SUCCESS,
		detail
	)


func set_failure(
	detail: String
) -> void:
	failures_value.text = "1"

	_set_state(
		STATE_FAILURE,
		detail
	)


func set_waiting_for_backend(
	detail: String = ""
) -> void:
	_set_state(
		STATE_WAITING_BACKEND,
		detail
	)


func get_ingestion_payload() -> Dictionary:
	return _build_ingestion_payload()


func get_state() -> String:
	return workflow_state
