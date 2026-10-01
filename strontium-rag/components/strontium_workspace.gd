class_name StrontiumWorkspace
extends Control


signal destination_displayed(destination_id: String)
signal destination_failed(destination_id: String, detail: String)


const SCREEN_HOST_NAME: String = "ScreenHost"
const SCROLL_CONTAINER_NAME: String = "WorkspaceScrollContainer"

const WORKSPACE_MIN_HEIGHT: float = 1100.0
const SCROLLBAR_WIDTH: float = 10.0
const CONTENT_MARGIN: float = 32.0


var navigation_service: NavigationService = null
var screen_registry: ScreenRegistry = null

var scroll_container: ScrollContainer = null
var screen_host: Control = null

var current_destination_id: String = ""
var current_screen: Node = null


func _ready() -> void:
	set_anchors_and_offsets_preset(
		Control.PRESET_FULL_RECT
	)

	mouse_filter = Control.MOUSE_FILTER_PASS

	_build_workspace()

	call_deferred(
		"_auto_configure"
	)


func _build_workspace() -> void:
	for child in get_children():
		child.queue_free()

	scroll_container = ScrollContainer.new()

	scroll_container.name = (
		SCROLL_CONTAINER_NAME
	)

	scroll_container.set_anchors_and_offsets_preset(
		Control.PRESET_FULL_RECT
	)

	scroll_container.horizontal_scroll_mode = (
		ScrollContainer.SCROLL_MODE_DISABLED
	)

	scroll_container.vertical_scroll_mode = (
		ScrollContainer.SCROLL_MODE_AUTO
	)

	scroll_container.follow_focus = true

	scroll_container.mouse_filter = (
		Control.MOUSE_FILTER_PASS
	)

	add_child(
		scroll_container
	)

	screen_host = Control.new()

	screen_host.name = SCREEN_HOST_NAME

	screen_host.position = Vector2.ZERO

	screen_host.custom_minimum_size = Vector2(
		0.0,
		WORKSPACE_MIN_HEIGHT
	)

	screen_host.mouse_filter = (
		Control.MOUSE_FILTER_PASS
	)

	scroll_container.add_child(
		screen_host
	)

	call_deferred(
		"_synchronize_workspace_size"
	)

	_style_scrollbar()


func _auto_configure() -> void:
	if navigation_service == null:
		navigation_service = _find_navigation_service()

	if screen_registry == null:
		screen_registry = _find_screen_registry()

	if navigation_service == null:
		return

	if not navigation_service.navigation_changed.is_connected(
		_on_navigation_changed
	):
		navigation_service.navigation_changed.connect(
			_on_navigation_changed
		)

	var destination_value: Variant = (
		navigation_service.get_current_destination()
	)

	if destination_value is Dictionary:
		display_destination(
			destination_value,
			""
		)

	elif destination_value is String:
		var destination_string: String = (
			str(destination_value)
		)

		if destination_string.is_empty():
			display_destination(
				ScreenRegistry.HOME,
				""
			)
		else:
			display_destination(
				destination_string,
				""
			)

	else:
		display_destination(
			ScreenRegistry.HOME,
			""
		)


func configure(
	service: NavigationService = null,
	registry: ScreenRegistry = null
) -> void:
	if service != null:
		navigation_service = service

	if registry != null:
		screen_registry = registry

	call_deferred(
		"_auto_configure"
	)


func _find_navigation_service() -> NavigationService:
	var current_scene: Node = (
		get_tree().current_scene
	)

	if current_scene == null:
		return null

	var node: Node = (
		current_scene.get_node_or_null(
			"NavigationService"
		)
	)

	if node is NavigationService:
		return node

	return null


func _find_screen_registry() -> ScreenRegistry:
	var current_scene: Node = (
		get_tree().current_scene
	)

	if current_scene == null:
		return null

	var node: Node = (
		current_scene.get_node_or_null(
			"ScreenRegistry"
		)
	)

	if node is ScreenRegistry:
		return node

	return null


func _on_navigation_changed(
	destination_id: String,
	title: String
) -> void:
	display_destination(
		destination_id,
		title
	)


func display_destination(
	destination: Variant,
	title: String = ""
) -> bool:
	if screen_host == null:
		return false

	var destination_id: String = ""
	var resolved_title: String = title

	if destination is Dictionary:
		var definition: Dictionary = destination

		var raw_id: Variant = (
			definition.get(
				"id",
				""
			)
		)

		if raw_id is String:
			destination_id = raw_id

		if resolved_title.is_empty():
			var raw_title: Variant = (
				definition.get(
					"title",
					""
				)
			)

			if raw_title is String:
				resolved_title = raw_title

	elif destination is String:
		destination_id = destination

	if destination_id.is_empty():
		return false

	_clear_current_screen()

	current_destination_id = destination_id

	if screen_registry == null:
		screen_registry = _find_screen_registry()

	if screen_registry == null:
		_show_destination_error(
			destination_id,
			"Screen registry is unavailable."
		)

		return false

	var code_screen: Control = (
		_build_code_screen(
			destination_id
		)
	)

	if code_screen != null:
		screen_host.add_child(
			code_screen
		)

		current_screen = code_screen

		_update_screen_host_size()

		destination_displayed.emit(
			destination_id
		)

		return true

	var scene_path: String = (
		screen_registry.get_scene_path(
			destination_id
		)
	)

	if not scene_path.is_empty():
		return _load_destination_scene(
			destination_id,
			scene_path
		)

	return _build_registered_workspace(
		destination_id,
		resolved_title
	)


func _build_code_screen(
	destination_id: String
) -> Control:
	match destination_id:
		ScreenRegistry.INGEST:
			var ingestion: StrontiumIngestion = (
				StrontiumIngestion.new()
			)

			ingestion.name = "Ingestion"

			ingestion.set_anchors_and_offsets_preset(
				Control.PRESET_FULL_RECT
			)

			return ingestion

		ScreenRegistry.KNOWLEDGE_BASE:
			var knowledge_base: StrontiumKnowledgeBase = (
				StrontiumKnowledgeBase.new()
			)

			knowledge_base.name = "KnowledgeBase"

			knowledge_base.set_anchors_and_offsets_preset(
				Control.PRESET_FULL_RECT
			)

			return knowledge_base

		ScreenRegistry.CHAT:
			var chat: StrontiumChat = (
				StrontiumChat.new()
			)

			chat.name = "Chat"

			chat.set_anchors_and_offsets_preset(
				Control.PRESET_FULL_RECT
			)

			return chat

		ScreenRegistry.EVALUATION:
			var evaluation: StrontiumEvaluation = (
				StrontiumEvaluation.new()
			)

			evaluation.name = "Evaluation"

			evaluation.set_anchors_and_offsets_preset(
				Control.PRESET_FULL_RECT
			)

			return evaluation

	return null


func _load_destination_scene(
	destination_id: String,
	scene_path: String
) -> bool:
	if not ResourceLoader.exists(
		scene_path
	):
		_show_destination_error(
			destination_id,
			"Scene does not exist: %s" % scene_path
		)

		return false

	var packed_scene: PackedScene = load(
		scene_path
	)

	if packed_scene == null:
		_show_destination_error(
			destination_id,
			"Unable to load scene: %s" % scene_path
		)

		return false

	var instance: Node = (
		packed_scene.instantiate()
	)

	if instance == null:
		_show_destination_error(
			destination_id,
			"Unable to instantiate scene: %s" % scene_path
		)

		return false

	screen_host.add_child(
		instance
	)

	current_screen = instance

	_update_screen_host_size()

	destination_displayed.emit(
		destination_id
	)

	return true


func _build_registered_workspace(
	destination_id: String,
	resolved_title: String
) -> bool:
	if screen_registry == null:
		return false

	var title_text: String = resolved_title

	if title_text.is_empty():
		title_text = screen_registry.get_title(
			destination_id
		)

	var subtitle: String = (
		screen_registry.get_subtitle(
			destination_id
		)
	)

	var panel: PanelContainer = PanelContainer.new()

	panel.name = "RegisteredWorkspace"

	panel.position = Vector2(
		CONTENT_MARGIN,
		CONTENT_MARGIN
	)

	panel.size = Vector2(
		screen_container_width() - (
			CONTENT_MARGIN * 2.0
		),
		WORKSPACE_MIN_HEIGHT - (
			CONTENT_MARGIN * 2.0
		)
	)

	panel.custom_minimum_size = panel.size

	panel.mouse_filter = (
		Control.MOUSE_FILTER_PASS
	)

	screen_host.add_child(
		panel
	)

	var content: VBoxContainer = VBoxContainer.new()

	content.position = Vector2(
		28.0,
		28.0
	)

	content.size = panel.size - Vector2(
		56.0,
		56.0
	)

	content.add_theme_constant_override(
		"separation",
		14
	)

	panel.add_child(
		content
	)

	var title_label: Label = Label.new()

	title_label.text = (
		title_text.to_upper()
	)

	title_label.add_theme_font_size_override(
		"font_size",
		28
	)

	title_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_PRIMARY
	)

	title_label.mouse_filter = (
		Control.MOUSE_FILTER_IGNORE
	)

	content.add_child(
		title_label
	)

	var subtitle_label: Label = Label.new()

	subtitle_label.text = subtitle

	subtitle_label.add_theme_font_size_override(
		"font_size",
		14
	)

	subtitle_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	subtitle_label.autowrap_mode = (
		TextServer.AUTOWRAP_WORD_SMART
	)

	subtitle_label.mouse_filter = (
		Control.MOUSE_FILTER_IGNORE
	)

	content.add_child(
		subtitle_label
	)

	var status_label: Label = Label.new()

	status_label.text = (
		"WORKSPACE INITIALIZED"
	)

	status_label.add_theme_font_size_override(
		"font_size",
		12
	)

	status_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	status_label.mouse_filter = (
		Control.MOUSE_FILTER_IGNORE
	)

	content.add_child(
		status_label
	)

	current_screen = panel

	_update_screen_host_size()

	destination_displayed.emit(
		destination_id
	)

	return true


func _show_destination_error(
	destination_id: String,
	detail: String
) -> void:
	if screen_host == null:
		return

	var panel: PanelContainer = PanelContainer.new()

	panel.name = "DestinationError"

	panel.position = Vector2(
		CONTENT_MARGIN,
		CONTENT_MARGIN
	)

	panel.size = Vector2(
		screen_container_width() - (
			CONTENT_MARGIN * 2.0
		),
		300.0
	)

	panel.custom_minimum_size = panel.size

	screen_host.add_child(
		panel
	)

	var content: VBoxContainer = VBoxContainer.new()

	content.position = Vector2(
		24.0,
		24.0
	)

	content.size = panel.size - Vector2(
		48.0,
		48.0
	)

	content.add_theme_constant_override(
		"separation",
		12
	)

	panel.add_child(
		content
	)

	var title_label: Label = Label.new()

	title_label.text = (
		"DESTINATION UNAVAILABLE"
	)

	title_label.add_theme_font_size_override(
		"font_size",
		24
	)

	title_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_PRIMARY
	)

	content.add_child(
		title_label
	)

	var destination_label: Label = Label.new()

	destination_label.text = destination_id

	destination_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	content.add_child(
		destination_label
	)

	var detail_label: Label = Label.new()

	detail_label.text = detail

	detail_label.autowrap_mode = (
		TextServer.AUTOWRAP_WORD_SMART
	)

	detail_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	content.add_child(
		detail_label
	)

	current_screen = panel

	_update_screen_host_size()

	destination_failed.emit(
		destination_id,
		detail
	)


func _clear_current_screen() -> void:
	if current_screen != null:
		if is_instance_valid(
			current_screen
		):
			current_screen.queue_free()

	current_screen = null

	if screen_host == null:
		return

	for child in screen_host.get_children():
		child.queue_free()


func _update_screen_host_size() -> void:
	if screen_host == null:
		return

	var required_width: float = (
		screen_container_width()
	)

	var required_height: float = (
		WORKSPACE_MIN_HEIGHT
	)

	screen_host.custom_minimum_size = Vector2(
		required_width,
		required_height
	)

	screen_host.size = Vector2(
		required_width,
		required_height
	)


func screen_container_width() -> float:
	if scroll_container == null:
		return 960.0

	return maxf(
		scroll_container.size.x - (
			SCROLLBAR_WIDTH + 4.0
		),
		640.0
	)


func _synchronize_workspace_size() -> void:
	if scroll_container == null:
		return

	if screen_host == null:
		return

	_update_screen_host_size()


func _style_scrollbar() -> void:
	if scroll_container == null:
		return

	var vertical_scrollbar: VScrollBar = (
		scroll_container.get_v_scroll_bar()
	)

	if vertical_scrollbar == null:
		return

	vertical_scrollbar.custom_minimum_size = Vector2(
		SCROLLBAR_WIDTH,
		0.0
	)

	var scroll_style: StyleBoxFlat = StyleBoxFlat.new()

	scroll_style.bg_color = Color(
		0.03,
		0.04,
		0.07,
		0.80
	)

	scroll_style.corner_radius_top_left = 5
	scroll_style.corner_radius_top_right = 5
	scroll_style.corner_radius_bottom_left = 5
	scroll_style.corner_radius_bottom_right = 5

	vertical_scrollbar.add_theme_stylebox_override(
		"scroll",
		scroll_style
	)

	var grabber_style: StyleBoxFlat = StyleBoxFlat.new()

	grabber_style.bg_color = Color(
		0.20,
		0.75,
		0.95,
		0.45
	)

	grabber_style.corner_radius_top_left = 5
	grabber_style.corner_radius_top_right = 5
	grabber_style.corner_radius_bottom_left = 5
	grabber_style.corner_radius_bottom_right = 5

	vertical_scrollbar.add_theme_stylebox_override(
		"grabber",
		grabber_style
	)

	var highlight_style: StyleBoxFlat = StyleBoxFlat.new()

	highlight_style.bg_color = Color(
		0.25,
		0.85,
		1.00,
		0.80
	)

	highlight_style.corner_radius_top_left = 5
	highlight_style.corner_radius_top_right = 5
	highlight_style.corner_radius_bottom_left = 5
	highlight_style.corner_radius_bottom_right = 5

	vertical_scrollbar.add_theme_stylebox_override(
		"grabber_highlight",
		highlight_style
	)

	var pressed_style: StyleBoxFlat = StyleBoxFlat.new()

	pressed_style.bg_color = Color(
		0.55,
		0.35,
		0.95,
		0.90
	)

	pressed_style.corner_radius_top_left = 5
	pressed_style.corner_radius_top_right = 5
	pressed_style.corner_radius_bottom_left = 5
	pressed_style.corner_radius_bottom_right = 5

	vertical_scrollbar.add_theme_stylebox_override(
		"grabber_pressed",
		pressed_style
	)


func navigate_to(
	destination_id: String
) -> bool:
	if navigation_service == null:
		navigation_service = (
			_find_navigation_service()
		)

	if navigation_service == null:
		return false

	return navigation_service.navigate_to(
		destination_id
	)


func show_destination(
	destination_id: String
) -> void:
	display_destination(
		destination_id,
		""
	)


func get_current_destination() -> String:
	return current_destination_id


func get_screen_host() -> Control:
	return screen_host


func get_scroll_container() -> ScrollContainer:
	return scroll_container


func _notification(
	what: int
) -> void:
	if what != NOTIFICATION_RESIZED:
		return

	call_deferred(
		"_synchronize_workspace_size"
	)
