class_name StrontiumHome
extends Control


const PAGE_MARGIN: float = 32.0
const SECTION_GAP: float = 20.0
const METRIC_HEIGHT: float = 120.0
const PANEL_HEIGHT: float = 220.0
const QUICK_ACTION_HEIGHT: float = 52.0


var content_root: Control

var title_label: Label
var subtitle_label: Label

var documents_metric: StrontiumMetricTile
var chunks_metric: StrontiumMetricTile
var system_metric: StrontiumMetricTile
var evaluation_metric: StrontiumMetricTile

var activity_panel: StrontiumPanel
var activity_title: Label
var activity_detail: Label
var activity_status: Label

var system_panel: StrontiumPanel
var system_title: Label
var system_detail: Label
var system_state: Label

var actions_panel: StrontiumPanel
var ingest_button: Button
var knowledge_button: Button
var chat_button: Button
var evaluation_button: Button


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_STOP
	_build_home()
	_update_layout()


func _notification(
	what: int
) -> void:
	if what == NOTIFICATION_RESIZED:
		_update_layout()


func _build_home() -> void:
	_clear_home()

	content_root = Control.new()
	content_root.name = "HomeContent"
	content_root.position = Vector2.ZERO
	content_root.size = size
	content_root.mouse_filter = (
		Control.MOUSE_FILTER_IGNORE
	)
	add_child(content_root)

	_build_header()
	_build_metrics()
	_build_activity_panel()
	_build_system_panel()
	_build_actions_panel()


func _clear_home() -> void:
	for child in get_children():
		if is_instance_valid(child):
			child.queue_free()


func _build_header() -> void:
	title_label = Label.new()
	title_label.name = "HomeTitle"
	title_label.text = "STRONTIUM RAG"
	title_label.position = Vector2(
		PAGE_MARGIN,
		PAGE_MARGIN
	)
	title_label.size = Vector2(
		760.0,
		42.0
	)
	title_label.modulate = (
		StrontiumTokens.TEXT_PRIMARY
	)
	title_label.add_theme_font_size_override(
		"font_size",
		32
	)
	title_label.mouse_filter = (
		Control.MOUSE_FILTER_IGNORE
	)

	content_root.add_child(
		title_label
	)

	subtitle_label = Label.new()
	subtitle_label.name = "HomeSubtitle"
	subtitle_label.text = (
		"Command center for retrieval, "
		+ "knowledge, evaluation, and system state."
	)
	subtitle_label.position = Vector2(
		PAGE_MARGIN,
		PAGE_MARGIN + 46.0
	)
	subtitle_label.size = Vector2(
		900.0,
		32.0
	)
	subtitle_label.modulate = (
		StrontiumTokens.TEXT_SECONDARY
	)
	subtitle_label.add_theme_font_size_override(
		"font_size",
		15
	)
	subtitle_label.mouse_filter = (
		Control.MOUSE_FILTER_IGNORE
	)

	content_root.add_child(
		subtitle_label
	)


func _build_metrics() -> void:
	documents_metric = (
		StrontiumMetricTile.new()
	)
	documents_metric.name = "DocumentsMetric"
	documents_metric.set_metric(
		"DOCUMENTS",
		"—",
		"Backend data pending"
	)

	content_root.add_child(
		documents_metric
	)

	chunks_metric = (
		StrontiumMetricTile.new()
	)
	chunks_metric.name = "ChunksMetric"
	chunks_metric.set_metric(
		"CHUNKS",
		"—",
		"Backend data pending"
	)

	content_root.add_child(
		chunks_metric
	)

	system_metric = (
		StrontiumMetricTile.new()
	)
	system_metric.name = "SystemMetric"
	system_metric.set_metric(
		"SYSTEM",
		"READY",
		"Godot application shell active"
	)

	content_root.add_child(
		system_metric
	)

	evaluation_metric = (
		StrontiumMetricTile.new()
	)
	evaluation_metric.name = "EvaluationMetric"
	evaluation_metric.set_metric(
		"EVALUATION",
		"—",
		"Evaluation service pending"
	)

	content_root.add_child(
		evaluation_metric
	)


func _build_activity_panel() -> void:
	activity_panel = (
		StrontiumPanel.new()
	)
	activity_panel.name = "ActivityPanel"
	activity_panel.glow_enabled = false

	content_root.add_child(
		activity_panel
	)

	activity_title = Label.new()
	activity_title.name = "ActivityTitle"
	activity_title.text = "RECENT ACTIVITY"
	activity_title.position = Vector2(
		20.0,
		16.0
	)
	activity_title.size = Vector2(
		400.0,
		30.0
	)
	activity_title.modulate = (
		StrontiumTokens.TEXT_PRIMARY
	)
	activity_title.add_theme_font_size_override(
		"font_size",
		18
	)
	activity_title.mouse_filter = (
		Control.MOUSE_FILTER_IGNORE
	)

	activity_panel.add_child(
		activity_title
	)

	activity_detail = Label.new()
	activity_detail.name = "ActivityDetail"
	activity_detail.text = (
		"No backend operations have been "
		+ "recorded in this session."
	)
	activity_detail.position = Vector2(
		20.0,
		60.0
	)
	activity_detail.size = Vector2(
		760.0,
		40.0
	)
	activity_detail.modulate = (
		StrontiumTokens.TEXT_SECONDARY
	)
	activity_detail.add_theme_font_size_override(
		"font_size",
		14
	)
	activity_detail.mouse_filter = (
		Control.MOUSE_FILTER_IGNORE
	)

	activity_panel.add_child(
		activity_detail
	)

	activity_status = Label.new()
	activity_status.name = "ActivityStatus"
	activity_status.text = (
		"WAITING FOR PYTHON INTEGRATION"
	)
	activity_status.position = Vector2(
		20.0,
		112.0
	)
	activity_status.size = Vector2(
		520.0,
		30.0
	)
	activity_status.modulate = (
		StrontiumTokens.TEXT_SECONDARY
	)
	activity_status.add_theme_font_size_override(
		"font_size",
		12
	)
	activity_status.mouse_filter = (
		Control.MOUSE_FILTER_IGNORE
	)

	activity_panel.add_child(
		activity_status
	)


func _build_system_panel() -> void:
	system_panel = (
		StrontiumPanel.new()
	)
	system_panel.name = "SystemPanel"
	system_panel.glow_enabled = true

	content_root.add_child(
		system_panel
	)

	system_title = Label.new()
	system_title.name = "SystemTitle"
	system_title.text = "SYSTEM STATE"
	system_title.position = Vector2(
		20.0,
		16.0
	)
	system_title.size = Vector2(
		400.0,
		30.0
	)
	system_title.modulate = (
		StrontiumTokens.TEXT_PRIMARY
	)
	system_title.add_theme_font_size_override(
		"font_size",
		18
	)
	system_title.mouse_filter = (
		Control.MOUSE_FILTER_IGNORE
	)

	system_panel.add_child(
		system_title
	)

	system_detail = Label.new()
	system_detail.name = "SystemDetail"
	system_detail.text = (
		"Godot application architecture is "
		+ "running. Python RAG integration has "
		+ "not yet been established."
	)
	system_detail.position = Vector2(
		20.0,
		60.0
	)
	system_detail.size = Vector2(
		760.0,
		56.0
	)
	system_detail.modulate = (
		StrontiumTokens.TEXT_SECONDARY
	)
	system_detail.add_theme_font_size_override(
		"font_size",
		14
	)
	system_detail.autowrap_mode = (
		TextServer.AUTOWRAP_WORD_SMART
	)
	system_detail.mouse_filter = (
		Control.MOUSE_FILTER_IGNORE
	)

	system_panel.add_child(
		system_detail
	)

	system_state = Label.new()
	system_state.name = "SystemState"
	system_state.text = (
		"APPLICATION SHELL ACTIVE"
	)
	system_state.position = Vector2(
		20.0,
		132.0
	)
	system_state.size = Vector2(
		500.0,
		30.0
	)
	system_state.modulate = (
		StrontiumTokens.TEXT_PRIMARY
	)
	system_state.add_theme_font_size_override(
		"font_size",
		13
	)
	system_state.mouse_filter = (
		Control.MOUSE_FILTER_IGNORE
	)

	system_panel.add_child(
		system_state
	)


func _build_actions_panel() -> void:
	actions_panel = (
		StrontiumPanel.new()
	)
	actions_panel.name = "QuickActionsPanel"
	actions_panel.glow_enabled = false

	content_root.add_child(
		actions_panel
	)

	var actions_title: Label = Label.new()
	actions_title.name = "QuickActionsTitle"
	actions_title.text = "QUICK ACTIONS"
	actions_title.position = Vector2(
		20.0,
		16.0
	)
	actions_title.size = Vector2(
		400.0,
		30.0
	)
	actions_title.modulate = (
		StrontiumTokens.TEXT_PRIMARY
	)
	actions_title.add_theme_font_size_override(
		"font_size",
		18
	)
	actions_title.mouse_filter = (
		Control.MOUSE_FILTER_IGNORE
	)

	actions_panel.add_child(
		actions_title
	)

	ingest_button = Button.new()
	ingest_button.name = "IngestButton"
	ingest_button.text = "INGEST DOCUMENTS"
	ingest_button.position = Vector2(
		20.0,
		60.0
	)
	ingest_button.size = Vector2(
		210.0,
		QUICK_ACTION_HEIGHT
	)
	ingest_button.pressed.connect(
		_on_ingest_pressed
	)

	actions_panel.add_child(
		ingest_button
	)

	knowledge_button = Button.new()
	knowledge_button.name = "KnowledgeButton"
	knowledge_button.text = "KNOWLEDGE BASE"
	knowledge_button.position = Vector2(
		245.0,
		60.0
	)
	knowledge_button.size = Vector2(
		210.0,
		QUICK_ACTION_HEIGHT
	)
	knowledge_button.pressed.connect(
		_on_knowledge_pressed
	)

	actions_panel.add_child(
		knowledge_button
	)

	chat_button = Button.new()
	chat_button.name = "ChatButton"
	chat_button.text = "OPEN CHAT"
	chat_button.position = Vector2(
		470.0,
		60.0
	)
	chat_button.size = Vector2(
		210.0,
		QUICK_ACTION_HEIGHT
	)
	chat_button.pressed.connect(
		_on_chat_pressed
	)

	actions_panel.add_child(
		chat_button
	)

	evaluation_button = Button.new()
	evaluation_button.name = "EvaluationButton"
	evaluation_button.text = "VIEW EVALUATION"
	evaluation_button.position = Vector2(
		695.0,
		60.0
	)
	evaluation_button.size = Vector2(
		210.0,
		QUICK_ACTION_HEIGHT
	)
	evaluation_button.pressed.connect(
		_on_evaluation_pressed
	)

	actions_panel.add_child(
		evaluation_button
	)


func _update_layout() -> void:
	if content_root == null:
		return

	content_root.size = size

	var available_width: float = maxf(
		0.0,
		size.x - PAGE_MARGIN * 2.0
	)

	var metric_gap: float = 16.0
	var metric_width: float = maxf(
		0.0,
		(available_width - metric_gap * 3.0)
		/ 4.0
	)

	var metrics_y: float = (
		PAGE_MARGIN
		+ 94.0
	)

	_set_control_rect(
		documents_metric,
		Vector2(
			PAGE_MARGIN,
			metrics_y
		),
		Vector2(
			metric_width,
			METRIC_HEIGHT
		)
	)

	_set_control_rect(
		chunks_metric,
		Vector2(
			PAGE_MARGIN
			+ metric_width
			+ metric_gap,
			metrics_y
		),
		Vector2(
			metric_width,
			METRIC_HEIGHT
		)
	)

	_set_control_rect(
		system_metric,
		Vector2(
			PAGE_MARGIN
			+ (metric_width + metric_gap) * 2.0,
			metrics_y
		),
		Vector2(
			metric_width,
			METRIC_HEIGHT
		)
	)

	_set_control_rect(
		evaluation_metric,
		Vector2(
			PAGE_MARGIN
			+ (metric_width + metric_gap) * 3.0,
			metrics_y
		),
		Vector2(
			metric_width,
			METRIC_HEIGHT
		)
	)

	var lower_y: float = (
		metrics_y
		+ METRIC_HEIGHT
		+ SECTION_GAP
	)

	var lower_gap: float = 20.0
	var lower_width: float = (
		available_width - lower_gap
	) * 0.5

	_set_control_rect(
		activity_panel,
		Vector2(
			PAGE_MARGIN,
			lower_y
		),
		Vector2(
			lower_width,
			PANEL_HEIGHT
		)
	)

	_set_control_rect(
		system_panel,
		Vector2(
			PAGE_MARGIN
			+ lower_width
			+ lower_gap,
			lower_y
		),
		Vector2(
			lower_width,
			PANEL_HEIGHT
		)
	)

	var actions_y: float = (
		lower_y
		+ PANEL_HEIGHT
		+ SECTION_GAP
	)

	var actions_height: float = (
		maxf(
			150.0,
			size.y - actions_y - PAGE_MARGIN
		)
	)

	_set_control_rect(
		actions_panel,
		Vector2(
			PAGE_MARGIN,
			actions_y
		),
		Vector2(
			available_width,
			actions_height
		)
	)


func _set_control_rect(
	control: Control,
	position: Vector2,
	control_size: Vector2
) -> void:
	if control == null:
		return

	control.position = position
	control.size = control_size


func _navigate_to(
	destination_id: String
) -> void:
	var current_scene: Node = (
		get_tree().current_scene
	)

	if current_scene == null:
		return

	var navigation_node: Node = (
		current_scene.find_child(
			"NavigationService",
			true,
			false
		)
	)

	var navigation_service: NavigationService = (
		navigation_node as NavigationService
	)

	if navigation_service == null:
		return

	navigation_service.navigate_to(
		destination_id
	)


func _on_ingest_pressed() -> void:
	_navigate_to(
		ScreenRegistry.INGEST
	)


func _on_knowledge_pressed() -> void:
	_navigate_to(
		ScreenRegistry.KNOWLEDGE_BASE
	)


func _on_chat_pressed() -> void:
	_navigate_to(
		ScreenRegistry.CHAT
	)


func _on_evaluation_pressed() -> void:
	_navigate_to(
		ScreenRegistry.EVALUATION
	)
