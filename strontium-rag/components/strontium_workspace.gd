class_name StrontiumWorkspace
extends Control


const CONTENT_MARGIN: float = 32.0
const TITLE_HEIGHT: float = 52.0
const SUBTITLE_HEIGHT: float = 32.0


var screen_host: Control
var current_screen: Control
var current_destination_id: String = ""


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_STOP
	_create_screen_host()


func _create_screen_host() -> void:
	screen_host = Control.new()
	screen_host.name = "ScreenHost"
	screen_host.set_anchors_and_offsets_preset(
		Control.PRESET_FULL_RECT
	)
	screen_host.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(screen_host)


func display_destination(
	definition: Dictionary,
	scene_path: String
) -> bool:
	if definition.is_empty():
		return false

	var destination_id: String = str(
		definition.get(
			"id",
			""
		)
	)

	if destination_id.is_empty():
		return false

	current_destination_id = destination_id

	_clear_current_screen()

	if not scene_path.is_empty():
		var scene: PackedScene = (
			load(scene_path) as PackedScene
		)

		if scene != null:
			var instance: Node = scene.instantiate()

			var control_instance: Control = (
				instance as Control
			)

			if control_instance != null:
				current_screen = control_instance

				screen_host.add_child(
					current_screen
				)

				current_screen.set_anchors_and_offsets_preset(
					Control.PRESET_FULL_RECT
				)

				return true

			instance.queue_free()

	return _build_registered_workspace(
		definition
	)


func _build_registered_workspace(
	definition: Dictionary
) -> bool:
	var available_width: float = maxf(
		0.0,
		size.x - CONTENT_MARGIN * 2.0
	)

	var available_height: float = maxf(
		0.0,
		size.y - CONTENT_MARGIN * 2.0
	)

	var panel: StrontiumPanel = (
		StrontiumPanel.new()
	)

	panel.name = "RegisteredWorkspacePanel"
	panel.glow_enabled = true
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	panel.position = Vector2(
		CONTENT_MARGIN,
		CONTENT_MARGIN
	)
	panel.size = Vector2(
		available_width,
		available_height
	)

	screen_host.add_child(panel)

	var title: Label = Label.new()
	title.name = "DestinationTitle"
	title.text = str(
		definition.get(
			"title",
			"Workspace"
		)
	)
	title.position = Vector2(
		CONTENT_MARGIN,
		CONTENT_MARGIN
	)
	title.size = Vector2(
		maxf(
			0.0,
			panel.size.x - CONTENT_MARGIN * 2.0
		),
		TITLE_HEIGHT
	)
	title.modulate = StrontiumTokens.TEXT_PRIMARY
	title.add_theme_font_size_override(
		"font_size",
		32
	)

	panel.add_child(title)

	var subtitle: Label = Label.new()
	subtitle.name = "DestinationSubtitle"
	subtitle.text = str(
		definition.get(
			"subtitle",
			""
		)
	)
	subtitle.position = Vector2(
		CONTENT_MARGIN,
		CONTENT_MARGIN + 52.0
	)
	subtitle.size = Vector2(
		maxf(
			0.0,
			panel.size.x - CONTENT_MARGIN * 2.0
		),
		SUBTITLE_HEIGHT
	)
	subtitle.modulate = StrontiumTokens.TEXT_SECONDARY
	subtitle.add_theme_font_size_override(
		"font_size",
		16
	)

	panel.add_child(subtitle)

	var status_panel: StrontiumPanel = (
		StrontiumPanel.new()
	)

	status_panel.name = "WorkspaceStatus"
	status_panel.glow_enabled = false
	status_panel.position = Vector2(
		CONTENT_MARGIN,
		CONTENT_MARGIN + 130.0
	)
	status_panel.size = Vector2(
		maxf(
			0.0,
			panel.size.x - CONTENT_MARGIN * 2.0
		),
		96.0
	)

	panel.add_child(status_panel)

	var status_heading: Label = Label.new()
	status_heading.name = "StatusHeading"
	status_heading.text = (
		"NAVIGATION ROUTE ACTIVE"
	)
	status_heading.position = Vector2(
		20.0,
		12.0
	)
	status_heading.size = Vector2(
		maxf(
			0.0,
			status_panel.size.x - 40.0
		),
		30.0
	)
	status_heading.modulate = (
		StrontiumTokens.TEXT_PRIMARY
	)
	status_heading.add_theme_font_size_override(
		"font_size",
		18
	)

	status_panel.add_child(
		status_heading
	)

	var status_detail: Label = Label.new()
	status_detail.name = "StatusDetail"
	status_detail.text = (
		"This destination is registered in the "
		+ "Strontium navigation framework."
	)
	status_detail.position = Vector2(
		20.0,
		48.0
	)
	status_detail.size = Vector2(
		maxf(
			0.0,
			status_panel.size.x - 40.0
		),
		28.0
	)
	status_detail.modulate = (
		StrontiumTokens.TEXT_SECONDARY
	)
	status_detail.add_theme_font_size_override(
		"font_size",
		14
	)

	status_panel.add_child(
		status_detail
	)

	current_screen = panel

	return true


func _clear_current_screen() -> void:
	if current_screen == null:
		return

	if is_instance_valid(
		current_screen
	):
		current_screen.queue_free()

	current_screen = null


func get_current_destination() -> String:
	return current_destination_id
