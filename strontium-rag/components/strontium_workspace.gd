class_name StrontiumWorkspace
extends Control


var workspace_background: Panel
var workspace_frame: Panel


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_build_workspace()


func _build_workspace() -> void:
	_create_background()
	_create_frame()


func _create_background() -> void:
	workspace_background = Panel.new()
	workspace_background.name = "WorkspaceBackground"
	workspace_background.mouse_filter = Control.MOUSE_FILTER_IGNORE

	workspace_background.set_anchors_and_offsets_preset(
		Control.PRESET_FULL_RECT
	)

	var style := StyleBoxFlat.new()

	style.bg_color = StrontiumTokens.SURFACE_PRIMARY
	style.border_color = StrontiumTokens.BORDER_SUBTLE

	style.set_border_width(
		SIDE_LEFT,
		StrontiumTokens.BORDER_WIDTH_SUBTLE
	)
	style.set_border_width(
		SIDE_TOP,
		StrontiumTokens.BORDER_WIDTH_SUBTLE
	)
	style.set_border_width(
		SIDE_RIGHT,
		StrontiumTokens.BORDER_WIDTH_SUBTLE
	)
	style.set_border_width(
		SIDE_BOTTOM,
		StrontiumTokens.BORDER_WIDTH_SUBTLE
	)

	style.corner_radius_top_left = StrontiumTokens.RADIUS_LARGE
	style.corner_radius_top_right = StrontiumTokens.RADIUS_LARGE
	style.corner_radius_bottom_left = StrontiumTokens.RADIUS_LARGE
	style.corner_radius_bottom_right = StrontiumTokens.RADIUS_LARGE

	style.content_margin_left = StrontiumTokens.SPACE_LG
	style.content_margin_right = StrontiumTokens.SPACE_LG
	style.content_margin_top = StrontiumTokens.SPACE_LG
	style.content_margin_bottom = StrontiumTokens.SPACE_LG

	workspace_background.add_theme_stylebox_override(
		"panel",
		style
	)

	add_child(workspace_background)
	move_child(workspace_background, 0)


func _create_frame() -> void:
	workspace_frame = Panel.new()
	workspace_frame.name = "WorkspaceFrame"
	workspace_frame.mouse_filter = Control.MOUSE_FILTER_IGNORE

	workspace_frame.set_anchors_and_offsets_preset(
		Control.PRESET_FULL_RECT
	)

	workspace_frame.offset_left = 8.0
	workspace_frame.offset_top = 8.0
	workspace_frame.offset_right = -8.0
	workspace_frame.offset_bottom = -8.0

	var frame_style := StyleBoxFlat.new()

	frame_style.bg_color = Color.TRANSPARENT
	frame_style.border_color = StrontiumTokens.BORDER_SUBTLE

	frame_style.set_border_width(
		SIDE_LEFT,
		StrontiumTokens.BORDER_WIDTH_SUBTLE
	)
	frame_style.set_border_width(
		SIDE_TOP,
		StrontiumTokens.BORDER_WIDTH_SUBTLE
	)
	frame_style.set_border_width(
		SIDE_RIGHT,
		StrontiumTokens.BORDER_WIDTH_SUBTLE
	)
	frame_style.set_border_width(
		SIDE_BOTTOM,
		StrontiumTokens.BORDER_WIDTH_SUBTLE
	)

	frame_style.corner_radius_top_left = StrontiumTokens.RADIUS_STANDARD
	frame_style.corner_radius_top_right = StrontiumTokens.RADIUS_STANDARD
	frame_style.corner_radius_bottom_left = StrontiumTokens.RADIUS_STANDARD
	frame_style.corner_radius_bottom_right = StrontiumTokens.RADIUS_STANDARD

	workspace_frame.add_theme_stylebox_override(
		"panel",
		frame_style
	)

	add_child(workspace_frame)


func set_surface_color(color: Color) -> void:
	if workspace_background == null:
		return

	var style := workspace_background.get_theme_stylebox(
		"panel"
	) as StyleBoxFlat

	if style == null:
		return

	style.bg_color = color
