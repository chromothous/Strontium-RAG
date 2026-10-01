class_name StrontiumEvaluation
extends Control


signal run_selected(run: Dictionary)
signal refresh_requested()


const STATE_IDLE: String = "IDLE"
const STATE_LOADING: String = "LOADING"
const STATE_READY: String = "READY"
const STATE_WAITING_FOR_BACKEND: String = "WAITING FOR BACKEND"
const STATE_ERROR: String = "ERROR"


const CONTENT_MARGIN: float = 32.0
const PANEL_MARGIN: float = 20.0
const SECTION_GAP: int = 18
const METRIC_GAP: int = 12


var evaluation_runs: Array[Dictionary] = []
var selected_run: Dictionary = {}

var state: String = STATE_WAITING_FOR_BACKEND
var state_detail: String = (
	"Evaluation service has not provided any run data."
)


var root_content: VBoxContainer = null
var state_label: Label = null
var state_detail_label: Label = null
var runs_container: VBoxContainer = null
var metrics_container: GridContainer = null
var detail_container: VBoxContainer = null
var run_count_label: Label = null
var refresh_button: Button = null


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

	margin.name = "EvaluationMargin"

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

	scroll.name = "EvaluationScroll"

	scroll.horizontal_scroll_mode = (
		ScrollContainer.SCROLL_MODE_DISABLED
	)

	scroll.vertical_scroll_mode = (
		ScrollContainer.SCROLL_MODE_AUTO
	)

	scroll.follow_focus = true

	margin.add_child(scroll)

	root_content = VBoxContainer.new()

	root_content.name = "EvaluationContent"

	root_content.custom_minimum_size = Vector2(
		0.0,
		980.0
	)

	root_content.add_theme_constant_override(
		"separation",
		SECTION_GAP
	)

	scroll.add_child(root_content)

	_build_header()
	_build_metrics_panel()
	_build_runs_panel()
	_build_detail_panel()


func _build_header() -> void:
	var header: PanelContainer = _make_panel()

	header.name = "EvaluationHeader"

	header.custom_minimum_size = Vector2(
		0.0,
		150.0
	)

	root_content.add_child(header)

	var margin: MarginContainer = _make_margin_container(
		header,
		PANEL_MARGIN
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
		7
	)

	layout.add_child(text_content)

	var title: Label = Label.new()

	title.text = "EVALUATION"

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
		"Retrieval, context, generation, citation, "
		+ "and grounding evidence"
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


func _build_metrics_panel() -> void:
	var panel: PanelContainer = _make_panel()

	panel.name = "MetricsPanel"

	panel.custom_minimum_size = Vector2(
		0.0,
		155.0
	)

	root_content.add_child(panel)

	var margin: MarginContainer = _make_margin_container(
		panel,
		PANEL_MARGIN
	)

	var content: VBoxContainer = VBoxContainer.new()

	content.add_theme_constant_override(
		"separation",
		12
	)

	margin.add_child(content)

	var heading: Label = _make_section_heading(
		"SELECTED RUN METRICS"
	)

	content.add_child(heading)

	metrics_container = GridContainer.new()

	metrics_container.columns = 5

	metrics_container.add_theme_constant_override(
		"h_separation",
		METRIC_GAP
	)

	metrics_container.add_theme_constant_override(
		"v_separation",
		METRIC_GAP
	)

	content.add_child(metrics_container)

	var metric_names: Array[String] = [
		"RETRIEVAL",
		"CONTEXT",
		"GENERATION",
		"CITATION",
		"GROUNDING"
	]

	for metric_name in metric_names:
		metrics_container.add_child(
			_make_metric_card(metric_name)
		)


func _build_runs_panel() -> void:
	var panel: PanelContainer = _make_panel()

	panel.name = "RunsPanel"

	panel.custom_minimum_size = Vector2(
		0.0,
		300.0
	)

	root_content.add_child(panel)

	var margin: MarginContainer = _make_margin_container(
		panel,
		PANEL_MARGIN
	)

	var content: VBoxContainer = VBoxContainer.new()

	content.add_theme_constant_override(
		"separation",
		10
	)

	margin.add_child(content)

	var heading_row: HBoxContainer = HBoxContainer.new()

	content.add_child(heading_row)

	var heading: Label = _make_section_heading(
		"EVALUATION RUNS"
	)

	heading.size_flags_horizontal = (
		Control.SIZE_EXPAND_FILL
	)

	heading_row.add_child(heading)

	run_count_label = Label.new()

	run_count_label.add_theme_font_size_override(
		"font_size",
		12
	)

	run_count_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	heading_row.add_child(run_count_label)

	runs_container = VBoxContainer.new()

	runs_container.add_theme_constant_override(
		"separation",
		8
	)

	content.add_child(runs_container)


func _build_detail_panel() -> void:
	var panel: PanelContainer = _make_panel()

	panel.name = "DetailPanel"

	panel.custom_minimum_size = Vector2(
		0.0,
		420.0
	)

	root_content.add_child(panel)

	var margin: MarginContainer = _make_margin_container(
		panel,
		PANEL_MARGIN
	)

	detail_container = VBoxContainer.new()

	detail_container.add_theme_constant_override(
		"separation",
		10
	)

	margin.add_child(detail_container)


func _render() -> void:
	_render_state()
	_render_runs()
	_render_metrics()
	_render_details()


func _render_state() -> void:
	if state_label == null:
		return

	state_label.text = (
		"STATE: "
		+ state
	)

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


func _render_runs() -> void:
	if runs_container == null:
		return

	for child in runs_container.get_children():
		child.queue_free()

	if run_count_label != null:
		run_count_label.text = (
			str(evaluation_runs.size())
			+ " RUNS"
		)

	if evaluation_runs.is_empty():
		var empty: Label = Label.new()

		empty.text = (
			"NO EVALUATION RUNS AVAILABLE"
		)

		empty.add_theme_font_size_override(
			"font_size",
			14
		)

		empty.add_theme_color_override(
			"font_color",
			StrontiumTokens.TEXT_SECONDARY
		)

		empty.horizontal_alignment = (
			HORIZONTAL_ALIGNMENT_CENTER
		)

		empty.custom_minimum_size = Vector2(
			0.0,
			90.0
		)

		runs_container.add_child(empty)

		return

	for index in evaluation_runs.size():
		var run: Dictionary = evaluation_runs[index]

		var button: Button = _make_run_button(run)

		button.pressed.connect(
			_on_run_pressed.bind(index)
		)

		runs_container.add_child(button)


func _render_metrics() -> void:
	if metrics_container == null:
		return

	if metrics_container.get_child_count() != 5:
		return

	var names: Array[String] = [
		"retrieval",
		"context",
		"generation",
		"citation",
		"grounding"
	]

	for index in names.size():
		var card_node: Node = (
			metrics_container.get_child(index)
		)

		if not (card_node is PanelContainer):
			continue

		var card: PanelContainer = (
			card_node as PanelContainer
		)

		var value_node: Node = (
			card.get_node_or_null(
				"Margin/MetricContent/MetricValue"
			)
		)

		if value_node == null:
			continue

		if not (value_node is Label):
			continue

		var value_label: Label = (
			value_node as Label
		)

		value_label.text = _format_metric_value(
			selected_run.get(
				names[index],
				null
			)
		)


func _render_details() -> void:
	if detail_container == null:
		return

	for child in detail_container.get_children():
		child.queue_free()

	var heading: Label = _make_section_heading(
		"RUN DETAILS"
	)

	detail_container.add_child(heading)

	if selected_run.is_empty():
		var empty: Label = Label.new()

		empty.text = (
			"Select an evaluation run to inspect "
			+ "its results, grounding evidence, and failures."
		)

		empty.autowrap_mode = (
			TextServer.AUTOWRAP_WORD_SMART
		)

		empty.add_theme_font_size_override(
			"font_size",
			14
		)

		empty.add_theme_color_override(
			"font_color",
			StrontiumTokens.TEXT_SECONDARY
		)

		detail_container.add_child(empty)

		return

	_add_detail_row(
		"RUN ID",
		str(
			selected_run.get(
				"run_id",
				""
			)
		)
	)

	_add_detail_row(
		"STATUS",
		str(
			selected_run.get(
				"status",
				""
			)
		)
	)

	_add_detail_row(
		"CREATED",
		str(
			selected_run.get(
				"created_at",
				""
			)
		)
	)

	_add_detail_row(
		"QUERY COUNT",
		str(
			selected_run.get(
				"query_count",
				""
			)
		)
	)

	var summary: Variant = selected_run.get(
		"summary",
		""
	)

	if summary is String:
		if not str(summary).is_empty():
			_add_detail_block(
				"SUMMARY",
				str(summary)
			)

	var grounding_results: Variant = (
		selected_run.get(
			"grounding_results",
			[]
		)
	)

	_add_detail_block(
		"GROUNDING RESULTS",
		_format_collection(
			grounding_results
		)
	)

	var failures: Variant = (
		selected_run.get(
			"failures",
			[]
		)
	)

	_add_detail_block(
		"FAILURES",
		_format_collection(
			failures
		)
	)


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


func _make_margin_container(
	parent: Control,
	margin_size: float
) -> MarginContainer:
	var margin: MarginContainer = MarginContainer.new()

	margin.name = "Margin"

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


func _make_section_heading(
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


func _make_metric_card(
	metric_name: String
) -> PanelContainer:
	var panel: PanelContainer = _make_panel()

	panel.name = (
		metric_name.capitalize()
		+ "Metric"
	)

	panel.custom_minimum_size = Vector2(
		0.0,
		80.0
	)

	var margin: MarginContainer = (
		_make_margin_container(
			panel,
			10.0
		)
	)

	var content: VBoxContainer = VBoxContainer.new()

	content.name = "MetricContent"

	content.add_theme_constant_override(
		"separation",
		4
	)

	margin.add_child(content)

	var name_label: Label = Label.new()

	name_label.text = metric_name

	name_label.add_theme_font_size_override(
		"font_size",
		10
	)

	name_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	content.add_child(name_label)

	var value_label: Label = Label.new()

	value_label.name = "MetricValue"

	value_label.text = "—"

	value_label.add_theme_font_size_override(
		"font_size",
		22
	)

	value_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_PRIMARY
	)

	content.add_child(value_label)

	return panel


func _make_run_button(
	run: Dictionary
) -> Button:
	var button: Button = Button.new()

	button.alignment = (
		HORIZONTAL_ALIGNMENT_LEFT
	)

	button.custom_minimum_size = Vector2(
		0.0,
		54.0
	)

	button.text = _format_run_label(run)

	button.tooltip_text = (
		"Inspect evaluation run"
	)

	return button


func _format_run_label(
	run: Dictionary
) -> String:
	var run_id: String = str(
		run.get(
			"run_id",
			"UNKNOWN RUN"
		)
	)

	var status: String = str(
		run.get(
			"status",
			"UNKNOWN"
		)
	)

	var created: String = str(
		run.get(
			"created_at",
			""
		)
	)

	var result: String = (
		run_id
		+ "  |  "
		+ status
	)

	if not created.is_empty():
		result = (
			result
			+ "  |  "
			+ created
		)

	return result


func _format_metric_value(
	value: Variant
) -> String:
	if value == null:
		return "—"

	if value is Dictionary:
		var metric: Dictionary = value

		if metric.has("value"):
			return _format_metric_value(
				metric.get("value")
			)

		if metric.has("label"):
			return str(
				metric.get("label")
			)

	if value is float:
		return "%.3f" % float(value)

	if value is int:
		return str(value)

	return str(value)


func _format_collection(
	value: Variant
) -> String:
	if value == null:
		return "NONE PROVIDED"

	if value is Array:
		var items: Array = value

		if items.is_empty():
			return "NONE PROVIDED"

		var lines: Array[String] = []

		for item in items:
			lines.append(
				"• " + str(item)
			)

		return "\n".join(lines)

	if value is Dictionary:
		var dictionary: Dictionary = value

		if dictionary.is_empty():
			return "NONE PROVIDED"

		return JSON.stringify(
			dictionary
		)

	var text_value: String = str(value)

	if text_value.is_empty():
		return "NONE PROVIDED"

	return text_value


func _add_detail_row(
	label_text: String,
	value_text: String
) -> void:
	var row: HBoxContainer = HBoxContainer.new()

	row.add_theme_constant_override(
		"separation",
		12
	)

	detail_container.add_child(row)

	var label: Label = Label.new()

	label.text = label_text

	label.custom_minimum_size = Vector2(
		130.0,
		0.0
	)

	label.add_theme_font_size_override(
		"font_size",
		11
	)

	label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	row.add_child(label)

	var value: Label = Label.new()

	value.text = value_text

	value.size_flags_horizontal = (
		Control.SIZE_EXPAND_FILL
	)

	value.autowrap_mode = (
		TextServer.AUTOWRAP_WORD_SMART
	)

	value.add_theme_font_size_override(
		"font_size",
		13
	)

	value.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_PRIMARY
	)

	row.add_child(value)


func _add_detail_block(
	heading_text: String,
	body_text: String
) -> void:
	var heading: Label = Label.new()

	heading.text = heading_text

	heading.add_theme_font_size_override(
		"font_size",
		11
	)

	heading.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	detail_container.add_child(heading)

	var body: Label = Label.new()

	body.text = body_text

	body.autowrap_mode = (
		TextServer.AUTOWRAP_WORD_SMART
	)

	body.add_theme_font_size_override(
		"font_size",
		13
	)

	body.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_PRIMARY
	)

	detail_container.add_child(body)


func _on_run_pressed(
	index: int
) -> void:
	if index < 0 or index >= evaluation_runs.size():
		return

	selected_run = evaluation_runs[index].duplicate(
		true
	)

	_render_metrics()
	_render_details()

	run_selected.emit(
		selected_run.duplicate(true)
	)


func _on_refresh_pressed() -> void:
	refresh_requested.emit()


func set_evaluation_runs(
	new_runs: Array
) -> void:
	evaluation_runs.clear()

	for value in new_runs:
		if value is Dictionary:
			evaluation_runs.append(
				value.duplicate(true)
			)

	if evaluation_runs.is_empty():
		selected_run.clear()

		state = STATE_WAITING_FOR_BACKEND

		state_detail = (
			"Evaluation service has not provided "
			+ "any run data."
		)
	else:
		state = STATE_READY

		state_detail = (
			"Evaluation run data is available."
		)

	if selected_run.is_empty():
		if not evaluation_runs.is_empty():
			selected_run = (
				evaluation_runs[0].duplicate(true)
			)

	_render()


func set_selected_run(
	run: Dictionary
) -> void:
	selected_run = run.duplicate(true)

	_render_metrics()
	_render_details()


func set_state(
	new_state: String,
	detail: String = ""
) -> void:
	state = new_state

	if detail.is_empty():
		state_detail = ""
	else:
		state_detail = detail

	_render_state()


func set_error(
	detail: String
) -> void:
	state = STATE_ERROR
	state_detail = detail
	_render_state()


func clear_evaluation_data() -> void:
	evaluation_runs.clear()
	selected_run.clear()

	state = STATE_WAITING_FOR_BACKEND

	state_detail = (
		"Evaluation service has not provided "
		+ "any run data."
	)

	_render()


func get_evaluation_runs() -> Array[Dictionary]:
	return evaluation_runs.duplicate(true)


func get_selected_run() -> Dictionary:
	return selected_run.duplicate(true)


func get_state() -> String:
	return state
