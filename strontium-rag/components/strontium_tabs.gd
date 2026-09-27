class_name StrontiumTabs
extends TabBar


@export var tab_height: float = 40.0
@export var glow_enabled: bool = true
@export var underline_enabled: bool = true


var selected_transition: Tween
var underline: ColorRect


func _ready() -> void:
	_configure_tabs()
	_apply_theme_styles()
	_build_underline()
	_connect_tab_signals()
	_update_underline()


func _configure_tabs() -> void:
	mouse_filter = Control.MOUSE_FILTER_STOP

	custom_minimum_size = Vector2(
		0,
		tab_height
	)

	mouse_default_cursor_shape = (
		Control.CURSOR_POINTING_HAND
	)

	focus_mode = Control.FOCUS_ALL

	clip_tabs = false
	deselect_enabled = false
	drag_to_rearrange_enabled = false
	scrolling_enabled = true

	add_theme_font_size_override(
		"font_size",
		StrontiumTokens.FONT_SIZE_BODY
	)

	add_theme_color_override(
		"font_selected_color",
		StrontiumTokens.TEXT_PRIMARY
	)

	add_theme_color_override(
		"font_unselected_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	add_theme_color_override(
		"font_hovered_color",
		StrontiumTokens.ACCENT_PRIMARY
	)

	add_theme_color_override(
		"font_disabled_color",
		StrontiumTokens.INTERACTION_DISABLED
	)

	add_theme_color_override(
		"font_outline_color",
		Color.TRANSPARENT
	)

	add_theme_constant_override(
		"outline_size",
		0
	)


func _apply_theme_styles() -> void:
	add_theme_stylebox_override(
		"tab_unselected",
		_create_tab_style(
			StrontiumTokens.SURFACE_PRIMARY,
			StrontiumTokens.BORDER_SUBTLE,
			false
		)
	)

	add_theme_stylebox_override(
		"tab_hovered",
		_create_tab_style(
			StrontiumTokens.SURFACE_ELEVATED,
			StrontiumTokens.ACCENT_PRIMARY,
			false
		)
	)

	add_theme_stylebox_override(
		"tab_selected",
		_create_tab_style(
			StrontiumTokens.INTERACTION_ACTIVE,
			StrontiumTokens.ACCENT_PRIMARY,
			true
		)
	)

	add_theme_stylebox_override(
		"tab_disabled",
		_create_tab_style(
			StrontiumTokens.SURFACE_PRIMARY,
			StrontiumTokens.INTERACTION_DISABLED,
			false
		)
	)

	add_theme_stylebox_override(
		"tab_focus",
		_create_tab_style(
			StrontiumTokens.SURFACE_ELEVATED,
			StrontiumTokens.ACCENT_SECONDARY,
			false
		)
	)


func _create_tab_style(
	background: Color,
	border: Color,
	selected: bool
) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()

	style.bg_color = background
	style.border_color = border

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
		0
	)

	style.corner_radius_top_left = (
		StrontiumTokens.RADIUS_SMALL
	)

	style.corner_radius_top_right = (
		StrontiumTokens.RADIUS_SMALL
	)

	style.corner_radius_bottom_left = 0
	style.corner_radius_bottom_right = 0

	style.content_margin_left = (
		StrontiumTokens.SPACE_LG
	)

	style.content_margin_right = (
		StrontiumTokens.SPACE_LG
	)

	style.content_margin_top = (
		StrontiumTokens.SPACE_SM
	)

	style.content_margin_bottom = (
		StrontiumTokens.SPACE_SM
	)

	if selected and glow_enabled:
		style.shadow_color = Color(
			StrontiumTokens.ACCENT_PRIMARY,
			0.25
		)

		style.shadow_size = 7
	else:
		style.shadow_color = Color.TRANSPARENT
		style.shadow_size = 0

	return style


func _build_underline() -> void:
	if is_instance_valid(
		underline
	):
		return

	underline = ColorRect.new()
	underline.name = "SelectedUnderline"

	underline.mouse_filter = (
		Control.MOUSE_FILTER_IGNORE
	)

	underline.color = (
		StrontiumTokens.ACCENT_PRIMARY
	)

	underline.anchor_top = 1.0
	underline.anchor_bottom = 1.0

	underline.offset_top = -2.0
	underline.offset_bottom = 0.0

	add_child(underline)

	move_child(
		underline,
		get_child_count() - 1
	)


func _connect_tab_signals() -> void:
	if not tab_changed.is_connected(
		_on_tab_changed
	):
		tab_changed.connect(
			_on_tab_changed
		)


func _on_tab_changed(
	index: int
) -> void:
	if index < 0:
		_hide_underline()
		return

	_animate_selection_change()
	_update_underline()


func _update_underline() -> void:
	if not is_instance_valid(
		underline
	):
		return

	if not underline_enabled:
		_hide_underline()
		return

	var selected_index := current_tab

	if selected_index < 0:
		_hide_underline()
		return

	var tab_rect := get_tab_rect(
		selected_index
	)

	underline.position = Vector2(
		tab_rect.position.x,
		tab_rect.end.y - 2.0
	)

	underline.size = Vector2(
		tab_rect.size.x,
		2.0
	)

	underline.visible = true


func _hide_underline() -> void:
	if not is_instance_valid(
		underline
	):
		return

	underline.visible = false


func _animate_selection_change() -> void:
	if selected_transition != null:
		if selected_transition.is_valid():
			selected_transition.kill()

	selected_transition = create_tween()

	selected_transition.set_trans(
		Tween.TRANS_QUAD
	)

	selected_transition.set_ease(
		Tween.EASE_OUT
	)

	selected_transition.tween_property(
		self,
		"modulate:a",
		0.88,
		StrontiumTokens.MOTION_FAST
	)

	selected_transition.tween_property(
		self,
		"modulate:a",
		1.0,
		StrontiumTokens.MOTION_FAST
	)


func set_glow_enabled(
	enabled: bool
) -> void:
	glow_enabled = enabled
	_apply_theme_styles()


func is_glow_enabled() -> bool:
	return glow_enabled


func set_underline_enabled(
	enabled: bool
) -> void:
	underline_enabled = enabled
	_update_underline()


func is_underline_enabled() -> bool:
	return underline_enabled


func refresh_style() -> void:
	_apply_theme_styles()
	_update_underline()


func _notification(
	notification: int
) -> void:
	if notification == NOTIFICATION_RESIZED:
		_update_underline()
