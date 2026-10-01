class_name StrontiumDiagnostics
extends Control


signal component_selected(component: Dictionary)
signal operation_selected(operation: Dictionary)
signal error_selected(error: Dictionary)
signal warning_selected(warning: Dictionary)
signal refresh_requested()


const STATE_READY: String = "READY"
const STATE_WAITING_FOR_BACKEND: String = "WAITING FOR BACKEND"
const STATE_ERROR: String = "ERROR"

const CONTENT_MARGIN: float = 32.0
const PANEL_PADDING: float = 20.0
const SECTION_GAP: int = 18
const ITEM_GAP: int = 8


var state: String = STATE_WAITING_FOR_BACKEND
var state_detail: String = ""

var system_status: Dictionary = {}
var components: Array[Dictionary] = []
var processing_state: Dictionary = {}
var recent_operations: Array[Dictionary] = []
var errors: Array[Dictionary] = []
var warnings: Array[Dictionary] = []
var diagnostic_details: Dictionary = {}

var root_content: VBoxContainer = null
var state_label: Label = null
var state_detail_label: Label = null
var refresh_button: Button = null

var system_status_content: VBoxContainer = null
var components_content: VBoxContainer = null
var processing_content: VBoxContainer = null
var operations_content: VBoxContainer = null
var errors_content: VBoxContainer = null
var warnings_content: VBoxContainer = null
var diagnostics_content: VBoxContainer = null


func _ready() -> void:
	set_anchors_and_offsets_preset(
		Control.PRESET_FULL_RECT
	)

	mouse_filter = Control.MOUSE_FILTER_PASS

	_build_interface()
	_render()


func _build_interface() -> void:
	for child in get_children():
		child.queue_free()

	var margin: MarginContainer = MarginContainer.new()
	margin.name = "DiagnosticsMargin"
	margin.set_anchors_and_offsets_preset(
		Control.PRESET_FULL_RECT
	)
	margin.add_theme_constant_override(
		"margin_left",
		int(CONTENT_MARGIN)
	)
	margin.add_theme_constant_override(
		"margin_top",
		int(CONTENT_MARGIN)
	)
	margin.add_theme_constant_override(
		"margin_right",
		int(CONTENT_MARGIN)
	)
	margin.add_theme_constant_override(
		"margin_bottom",
		int(CONTENT_MARGIN)
	)
	add_child(margin)

	var scroll: ScrollContainer = ScrollContainer.new()
	scroll.name = "DiagnosticsScroll"
	scroll.horizontal_scroll_mode = (
		ScrollContainer.SCROLL_MODE_DISABLED
	)
	scroll.vertical_scroll_mode = (
		ScrollContainer.SCROLL_MODE_AUTO
	)
	scroll.follow_focus = true
	margin.add_child(scroll)

	root_content = VBoxContainer.new()
	root_content.name = "DiagnosticsContent"
	root_content.custom_minimum_size = Vector2(
		0.0,
		1150.0
	)
	root_content.add_theme_constant_override(
		"separation",
		SECTION_GAP
	)
	scroll.add_child(root_content)

	_build_header()
	_build_system_status_panel()
	_build_components_panel()
	_build_processing_panel()
	_build_operations_panel()
	_build_errors_panel()
	_build_warnings_panel()
	_build_details_panel()


func _build_header() -> void:
	var panel: PanelContainer = _make_panel()
	panel.name = "DiagnosticsHeader"
	panel.custom_minimum_size = Vector2(
		0.0,
		145.0
	)
	root_content.add_child(panel)

	var margin: MarginContainer = _make_margin(
		panel,
		PANEL_PADDING
	)

	var layout: HBoxContainer = HBoxContainer.new()
	layout.add_theme_constant_override(
		"separation",
		18
	)
	margin.add_child(layout)

	var text_content: VBoxContainer = VBoxContainer.new()
	text_content.size_flags_horizontal = (
		Control.SIZE_EXPAND_FILL
	)
	text_content.add_theme_constant_override(
		"separation",
		6
	)
	layout.add_child(text_content)

	var title: Label = Label.new()
	title.text = "DIAGNOSTICS"
	title.add_theme_font_size_override(
		"font_size",
		30
	)
	title.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_PRIMARY
	)
	text_content.add_child(title)

	var subtitle: Label = Label.new()
	subtitle.text = (
		"System status, component health, processing state, "
		+ "operations, errors, and diagnostic evidence"
	)
	subtitle.autowrap_mode = (
		TextServer.AUTOWRAP_WORD_SMART
	)
	subtitle.add_theme_font_size_override(
		"font_size",
		14
	)
	subtitle.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)
	text_content.add_child(subtitle)

	state_label = Label.new()
	state_label.add_theme_font_size_override(
		"font_size",
		12
	)
	text_content.add_child(state_label)

	state_detail_label = Label.new()
	state_detail_label.autowrap_mode = (
		TextServer.AUTOWRAP_WORD_SMART
	)
	state_detail_label.add_theme_font_size_override(
		"font_size",
		12
	)
	state_detail_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)
	text_content.add_child(state_detail_label)

	refresh_button = Button.new()
	refresh_button.text = "REFRESH"
	refresh_button.custom_minimum_size = Vector2(
		120.0,
		44.0
	)
	refresh_button.pressed.connect(
		_on_refresh_pressed
	)
	layout.add_child(refresh_button)


func _build_system_status_panel() -> void:
	var panel: PanelContainer = _make_panel()
	panel.name = "SystemStatusPanel"
	panel.custom_minimum_size = Vector2(
		0.0,
		170.0
	)
	root_content.add_child(panel)

	var margin: MarginContainer = _make_margin(
		panel,
		PANEL_PADDING
	)

	system_status_content = VBoxContainer.new()
	system_status_content.add_theme_constant_override(
		"separation",
		8
	)
	margin.add_child(system_status_content)

	var heading: Label = _make_heading(
		"SYSTEM STATUS"
	)
	system_status_content.add_child(heading)


func _build_components_panel() -> void:
	var panel: PanelContainer = _make_panel()
	panel.name = "ComponentsPanel"
	panel.custom_minimum_size = Vector2(
		0.0,
		280.0
	)
	root_content.add_child(panel)

	var margin: MarginContainer = _make_margin(
		panel,
		PANEL_PADDING
	)

	components_content = VBoxContainer.new()
	components_content.add_theme_constant_override(
		"separation",
		ITEM_GAP
	)
	margin.add_child(components_content)

	var heading: Label = _make_heading(
		"COMPONENT HEALTH"
	)
	components_content.add_child(heading)


func _build_processing_panel() -> void:
	var panel: PanelContainer = _make_panel()
	panel.name = "ProcessingPanel"
	panel.custom_minimum_size = Vector2(
		0.0,
		170.0
	)
	root_content.add_child(panel)

	var margin: MarginContainer = _make_margin(
		panel,
		PANEL_PADDING
	)

	processing_content = VBoxContainer.new()
	processing_content.add_theme_constant_override(
		"separation",
		8
	)
	margin.add_child(processing_content)

	var heading: Label = _make_heading(
		"PROCESSING STATE"
	)
	processing_content.add_child(heading)


func _build_operations_panel() -> void:
	var panel: PanelContainer = _make_panel()
	panel.name = "OperationsPanel"
	panel.custom_minimum_size = Vector2(
		0.0,
		260.0
	)
	root_content.add_child(panel)

	var margin: MarginContainer = _make_margin(
		panel,
		PANEL_PADDING
	)

	operations_content = VBoxContainer.new()
	operations_content.add_theme_constant_override(
		"separation",
		ITEM_GAP
	)
	margin.add_child(operations_content)

	var heading: Label = _make_heading(
		"RECENT OPERATIONS"
	)
	operations_content.add_child(heading)


func _build_errors_panel() -> void:
	var panel: PanelContainer = _make_panel()
	panel.name = "ErrorsPanel"
	panel.custom_minimum_size = Vector2(
		0.0,
		220.0
	)
	root_content.add_child(panel)

	var margin: MarginContainer = _make_margin(
		panel,
		PANEL_PADDING
	)

	errors_content = VBoxContainer.new()
	errors_content.add_theme_constant_override(
		"separation",
		ITEM_GAP
	)
	margin.add_child(errors_content)

	var heading: Label = _make_heading(
		"ERRORS"
	)
	errors_content.add_child(heading)


func _build_warnings_panel() -> void:
	var panel: PanelContainer = _make_panel()
	panel.name = "WarningsPanel"
	panel.custom_minimum_size = Vector2(
		0.0,
		220.0
	)
	root_content.add_child(panel)

	var margin: MarginContainer = _make_margin(
		panel,
		PANEL_PADDING
	)

	warnings_content = VBoxContainer.new()
	warnings_content.add_theme_constant_override(
		"separation",
		ITEM_GAP
	)
	margin.add_child(warnings_content)

	var heading: Label = _make_heading(
		"WARNINGS"
	)
	warnings_content.add_child(heading)


func _build_details_panel() -> void:
	var panel: PanelContainer = _make_panel()
	panel.name = "DiagnosticDetailsPanel"
	panel.custom_minimum_size = Vector2(
		0.0,
		300.0
	)
	root_content.add_child(panel)

	var margin: MarginContainer = _make_margin(
		panel,
		PANEL_PADDING
	)

	diagnostics_content = VBoxContainer.new()
	diagnostics_content.add_theme_constant_override(
		"separation",
		8
	)
	margin.add_child(diagnostics_content)

	var heading: Label = _make_heading(
		"DIAGNOSTIC INFORMATION"
	)
	diagnostics_content.add_child(heading)


func _render() -> void:
	_render_state()
	_render_system_status()
	_render_components()
	_render_processing()
	_render_operations()
	_render_errors()
	_render_warnings()
	_render_diagnostic_details()


func _render_state() -> void:
	if state_label == null:
		return

	state_label.text = "STATE: " + state

	if state == STATE_ERROR:
		state_label.add_theme_color_override(
			"font_color",
			Color(
				1.0,
				0.45,
				0.45,
				1.0
			)
		)
	else:
		state_label.add_theme_color_override(
			"font_color",
			Color(
				0.35,
				0.85,
				1.0,
				1.0
			)
		)

	state_detail_label.text = state_detail


func _render_system_status() -> void:
	if system_status_content == null:
		return

	_clear_dynamic_children(
		system_status_content
	)

	system_status_content.add_child(
		_make_heading("SYSTEM STATUS")
	)

	if system_status.is_empty():
		system_status_content.add_child(
			_make_empty_label(
				"NO SYSTEM STATUS AVAILABLE"
			)
		)
		return

	_add_dictionary_rows(
		system_status_content,
		system_status
	)


func _render_components() -> void:
	if components_content == null:
		return

	_clear_dynamic_children(
		components_content
	)

	components_content.add_child(
		_make_heading("COMPONENT HEALTH")
	)

	if components.is_empty():
		components_content.add_child(
			_make_empty_label(
				"NO COMPONENT HEALTH DATA AVAILABLE"
			)
		)
		return

	for component in components:
		var button: Button = _make_component_button(
			component
		)

		button.pressed.connect(
			_on_component_pressed.bind(
				component
			)
		)

		components_content.add_child(button)


func _render_processing() -> void:
	if processing_content == null:
		return

	_clear_dynamic_children(
		processing_content
	)

	processing_content.add_child(
		_make_heading("PROCESSING STATE")
	)

	if processing_state.is_empty():
		processing_content.add_child(
			_make_empty_label(
				"NO PROCESSING STATE AVAILABLE"
			)
		)
		return

	_add_dictionary_rows(
		processing_content,
		processing_state
	)


func _render_operations() -> void:
	if operations_content == null:
		return

	_clear_dynamic_children(
		operations_content
	)

	operations_content.add_child(
		_make_heading("RECENT OPERATIONS")
	)

	if recent_operations.is_empty():
		operations_content.add_child(
			_make_empty_label(
				"NO RECENT OPERATIONS AVAILABLE"
			)
		)
		return

	for operation in recent_operations:
		var button: Button = _make_operation_button(
			operation
		)

		button.pressed.connect(
			_on_operation_pressed.bind(
				operation
			)
		)

		operations_content.add_child(button)


func _render_errors() -> void:
	if errors_content == null:
		return

	_clear_dynamic_children(
		errors_content
	)

	errors_content.add_child(
		_make_heading("ERRORS")
	)

	if errors.is_empty():
		errors_content.add_child(
			_make_empty_label(
				"NO ERRORS REPORTED"
			)
		)
		return

	for error in errors:
		var button: Button = _make_issue_button(
			error,
			true
		)

		button.pressed.connect(
			_on_error_pressed.bind(
				error
			)
		)

		errors_content.add_child(button)


func _render_warnings() -> void:
	if warnings_content == null:
		return

	_clear_dynamic_children(
		warnings_content
	)

	warnings_content.add_child(
		_make_heading("WARNINGS")
	)

	if warnings.is_empty():
		warnings_content.add_child(
			_make_empty_label(
				"NO WARNINGS REPORTED"
			)
		)
		return

	for warning in warnings:
		var button: Button = _make_issue_button(
			warning,
			false
		)

		button.pressed.connect(
			_on_warning_pressed.bind(
				warning
			)
		)

		warnings_content.add_child(button)


func _render_diagnostic_details() -> void:
	if diagnostics_content == null:
		return

	_clear_dynamic_children(
		diagnostics_content
	)

	diagnostics_content.add_child(
		_make_heading("DIAGNOSTIC INFORMATION")
	)

	if diagnostic_details.is_empty():
		diagnostics_content.add_child(
			_make_empty_label(
				"NO DIAGNOSTIC DETAILS AVAILABLE"
			)
		)
		return

	_add_dictionary_rows(
		diagnostics_content,
		diagnostic_details
	)


func _clear_dynamic_children(
	container: VBoxContainer
) -> void:
	for child in container.get_children():
		child.queue_free()


func _add_dictionary_rows(
	container: VBoxContainer,
	data: Dictionary
) -> void:
	var keys: Array = data.keys()
	keys.sort()

	for key_value in keys:
		var key_text: String = str(key_value)
		var value_text: String = _format_value(
			data.get(key_value)
		)

		var row: HBoxContainer = HBoxContainer.new()
		row.add_theme_constant_override(
			"separation",
			12
		)
		container.add_child(row)

		var key_label: Label = Label.new()
		key_label.text = key_text.to_upper()
		key_label.custom_minimum_size = Vector2(
			150.0,
			0.0
		)
		key_label.add_theme_font_size_override(
			"font_size",
			11
		)
		key_label.add_theme_color_override(
			"font_color",
			StrontiumTokens.TEXT_SECONDARY
		)
		row.add_child(key_label)

		var value_label: Label = Label.new()
		value_label.text = value_text
		value_label.size_flags_horizontal = (
			Control.SIZE_EXPAND_FILL
		)
		value_label.autowrap_mode = (
			TextServer.AUTOWRAP_WORD_SMART
		)
		value_label.add_theme_font_size_override(
			"font_size",
			13
		)
		value_label.add_theme_color_override(
			"font_color",
			StrontiumTokens.TEXT_PRIMARY
		)
		row.add_child(value_label)


func _make_component_button(
	component: Dictionary
) -> Button:
	var button: Button = Button.new()
	button.alignment = HORIZONTAL_ALIGNMENT_LEFT
	button.custom_minimum_size = Vector2(
		0.0,
		54.0
	)

	var name_text: String = str(
		component.get(
			"name",
			"UNKNOWN COMPONENT"
		)
	)

	var status_text: String = str(
		component.get(
			"status",
			"UNKNOWN"
		)
	)

	var detail_text: String = str(
		component.get(
			"detail",
			""
		)
	)

	button.text = (
		name_text.to_upper()
		+ "  |  "
		+ status_text.to_upper()
	)

	if not detail_text.is_empty():
		button.tooltip_text = detail_text

	return button


func _make_operation_button(
	operation: Dictionary
) -> Button:
	var button: Button = Button.new()
	button.alignment = HORIZONTAL_ALIGNMENT_LEFT
	button.custom_minimum_size = Vector2(
		0.0,
		50.0
	)

	var name_text: String = str(
		operation.get(
			"operation",
			operation.get(
				"name",
				"UNKNOWN OPERATION"
			)
		)
	)

	var status_text: String = str(
		operation.get(
			"status",
			"UNKNOWN"
		)
	)

	var timestamp_text: String = str(
		operation.get(
			"timestamp",
			operation.get(
				"created_at",
				""
			)
		)
	)

	button.text = (
		name_text.to_upper()
		+ "  |  "
		+ status_text.to_upper()
	)

	if not timestamp_text.is_empty():
		button.text += "  |  " + timestamp_text

	return button


func _make_issue_button(
	issue: Dictionary,
	is_error: bool
) -> Button:
	var button: Button = Button.new()
	button.alignment = HORIZONTAL_ALIGNMENT_LEFT
	button.custom_minimum_size = Vector2(
		0.0,
		50.0
	)

	var message_text: String = str(
		issue.get(
			"message",
			issue.get(
				"detail",
				"No message provided"
			)
		)
	)

	var code_text: String = str(
		issue.get(
			"code",
			""
		)
	)

	var prefix: String = "ERROR"

	if not is_error:
		prefix = "WARNING"

	if code_text.is_empty():
		button.text = prefix + "  |  " + message_text
	else:
		button.text = (
			prefix
			+ "  |  "
			+ code_text
			+ "  |  "
			+ message_text
		)

	return button


func _make_empty_label(
	text_value: String
) -> Label:
	var label: Label = Label.new()
	label.text = text_value
	label.custom_minimum_size = Vector2(
		0.0,
		52.0
	)
	label.horizontal_alignment = (
		HORIZONTAL_ALIGNMENT_CENTER
	)
	label.vertical_alignment = (
		VERTICAL_ALIGNMENT_CENTER
	)
	label.add_theme_font_size_override(
		"font_size",
		12
	)
	label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)
	return label


func _make_heading(
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
		StrontiumTokens.TEXT_PRIMARY
	)
	return label


func _make_panel() -> PanelContainer:
	var panel: PanelContainer = PanelContainer.new()
	var style: StyleBoxFlat = StyleBoxFlat.new()

	style.bg_color = Color(
		0.055,
		0.065,
		0.10,
		0.96
	)
	style.border_width_left = 1
	style.border_width_top = 1
	style.border_width_right = 1
	style.border_width_bottom = 1
	style.border_color = Color(
		0.18,
		0.24,
		0.34,
		0.90
	)
	style.corner_radius_top_left = 8
	style.corner_radius_top_right = 8
	style.corner_radius_bottom_right = 8
	style.corner_radius_bottom_left = 8

	panel.add_theme_stylebox_override(
		"panel",
		style
	)

	return panel


func _make_margin(
	parent: Control,
	margin_size: float
) -> MarginContainer:
	var margin: MarginContainer = MarginContainer.new()

	margin.add_theme_constant_override(
		"margin_left",
		int(margin_size)
	)
	margin.add_theme_constant_override(
		"margin_top",
		int(margin_size)
	)
	margin.add_theme_constant_override(
		"margin_right",
		int(margin_size)
	)
	margin.add_theme_constant_override(
		"margin_bottom",
		int(margin_size)
	)

	parent.add_child(margin)

	return margin


func _format_value(
	value: Variant
) -> String:
	if value == null:
		return "—"

	if value is Dictionary:
		var dictionary: Dictionary = value

		if dictionary.is_empty():
			return "{}"

		return JSON.stringify(
			dictionary
		)

	if value is Array:
		var array_value: Array = value

		if array_value.is_empty():
			return "[]"

		return JSON.stringify(
			array_value
		)

	return str(value)


func _on_component_pressed(
	component: Dictionary
) -> void:
	component_selected.emit(
		component.duplicate(true)
	)


func _on_operation_pressed(
	operation: Dictionary
) -> void:
	operation_selected.emit(
		operation.duplicate(true)
	)


func _on_error_pressed(
	error: Dictionary
) -> void:
	error_selected.emit(
		error.duplicate(true)
	)


func _on_warning_pressed(
	warning: Dictionary
) -> void:
	warning_selected.emit(
		warning.duplicate(true)
	)


func _on_refresh_pressed() -> void:
	refresh_requested.emit()


func set_system_status(
	status: Dictionary
) -> void:
	system_status = status.duplicate(true)
	_set_ready_state()
	_render()


func set_components(
	new_components: Array
) -> void:
	components.clear()

	for value in new_components:
		if value is Dictionary:
			components.append(
				value.duplicate(true)
			)

	_set_ready_state()
	_render()


func set_processing_state(
	new_state: Dictionary
) -> void:
	processing_state = new_state.duplicate(true)
	_set_ready_state()
	_render()


func set_recent_operations(
	operations: Array
) -> void:
	recent_operations.clear()

	for value in operations:
		if value is Dictionary:
			recent_operations.append(
				value.duplicate(true)
			)

	_set_ready_state()
	_render()


func set_errors(
	new_errors: Array
) -> void:
	errors.clear()

	for value in new_errors:
		if value is Dictionary:
			errors.append(
				value.duplicate(true)
			)

	_set_ready_state()
	_render()


func set_warnings(
	new_warnings: Array
) -> void:
	warnings.clear()

	for value in new_warnings:
		if value is Dictionary:
			warnings.append(
				value.duplicate(true)
			)

	_set_ready_state()
	_render()


func set_diagnostic_details(
	details: Dictionary
) -> void:
	diagnostic_details = details.duplicate(true)
	_set_ready_state()
	_render()


func set_snapshot(
	snapshot: Dictionary
) -> void:
	system_status.clear()
	components.clear()
	processing_state.clear()
	recent_operations.clear()
	errors.clear()
	warnings.clear()
	diagnostic_details.clear()

	var raw_system_status: Variant = snapshot.get(
		"system_status",
		{}
	)

	if raw_system_status is Dictionary:
		system_status = raw_system_status.duplicate(true)

	var raw_components: Variant = snapshot.get(
		"components",
		[]
	)

	if raw_components is Array:
		for value in raw_components:
			if value is Dictionary:
				components.append(
					value.duplicate(true)
				)

	var raw_processing: Variant = snapshot.get(
		"processing_state",
		{}
	)

	if raw_processing is Dictionary:
		processing_state = raw_processing.duplicate(true)

	var raw_operations: Variant = snapshot.get(
		"recent_operations",
		[]
	)

	if raw_operations is Array:
		for value in raw_operations:
			if value is Dictionary:
				recent_operations.append(
					value.duplicate(true)
				)

	var raw_errors: Variant = snapshot.get(
		"errors",
		[]
	)

	if raw_errors is Array:
		for value in raw_errors:
			if value is Dictionary:
				errors.append(
					value.duplicate(true)
				)

	var raw_warnings: Variant = snapshot.get(
		"warnings",
		[]
	)

	if raw_warnings is Array:
		for value in raw_warnings:
			if value is Dictionary:
				warnings.append(
					value.duplicate(true)
				)

	var raw_details: Variant = snapshot.get(
		"diagnostic_details",
		{}
	)

	if raw_details is Dictionary:
		diagnostic_details = raw_details.duplicate(true)

	_set_ready_state()
	_render()


func set_state(
	new_state: String,
	detail: String = ""
) -> void:
	state = new_state
	state_detail = detail
	_render_state()


func set_error(
	detail: String
) -> void:
	state = STATE_ERROR
	state_detail = detail
	_render_state()


func clear_data() -> void:
	system_status.clear()
	components.clear()
	processing_state.clear()
	recent_operations.clear()
	errors.clear()
	warnings.clear()
	diagnostic_details.clear()

	state = STATE_WAITING_FOR_BACKEND
	state_detail = (
		"Diagnostic service has not provided any data."
	)

	_render()


func get_state() -> String:
	return state


func get_system_status() -> Dictionary:
	return system_status.duplicate(true)


func get_components() -> Array[Dictionary]:
	return components.duplicate(true)


func get_processing_state() -> Dictionary:
	return processing_state.duplicate(true)


func get_recent_operations() -> Array[Dictionary]:
	return recent_operations.duplicate(true)


func get_errors() -> Array[Dictionary]:
	return errors.duplicate(true)


func get_warnings() -> Array[Dictionary]:
	return warnings.duplicate(true)


func get_diagnostic_details() -> Dictionary:
	return diagnostic_details.duplicate(true)


func _set_ready_state() -> void:
	state = STATE_READY
	state_detail = (
		"Diagnostic data is available."
	)
