class_name StrontiumMenu
extends PopupMenu


signal menu_action_selected(id: int)


@export var glow_enabled: bool = true
@export var menu_width: int = 220
@export var item_height: int = 32


var menu_style: StyleBoxFlat
var hover_style: StyleBoxFlat


func _ready() -> void:
	_configure_menu()
	_build_styles()
	_apply_styles()

	if not id_pressed.is_connected(
		_on_id_pressed
	):
		id_pressed.connect(
			_on_id_pressed
	)


func _configure_menu() -> void:
	min_size = Vector2i(
		menu_width,
		0
	)

	add_theme_font_size_override(
		"font_size",
		14
	)

	add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_PRIMARY
	)

	add_theme_color_override(
		"font_hover_color",
		StrontiumTokens.TEXT_PRIMARY
	)

	add_theme_color_override(
		"font_pressed_color",
		StrontiumTokens.TEXT_PRIMARY
	)

	add_theme_color_override(
		"font_disabled_color",
		StrontiumTokens.INTERACTION_DISABLED
	)

	add_theme_constant_override(
		"item_start_padding",
		14
	)

	add_theme_constant_override(
		"item_end_padding",
		14
	)

	add_theme_constant_override(
		"v_separation",
		6
	)


func _build_styles() -> void:
	menu_style = StyleBoxFlat.new()

	menu_style.bg_color = (
		StrontiumTokens.BORDER_STANDARD.darkened(
			0.55
		)
	)

	menu_style.border_width_left = 1
	menu_style.border_width_top = 1
	menu_style.border_width_right = 1
	menu_style.border_width_bottom = 1

	menu_style.border_color = Color(
		StrontiumTokens.ACCENT_PRIMARY,
		0.45
	)

	menu_style.corner_radius_top_left = 8
	menu_style.corner_radius_top_right = 8
	menu_style.corner_radius_bottom_left = 8
	menu_style.corner_radius_bottom_right = 8

	menu_style.content_margin_left = 6
	menu_style.content_margin_top = 6
	menu_style.content_margin_right = 6
	menu_style.content_margin_bottom = 6

	if glow_enabled:
		menu_style.shadow_color = Color(
			StrontiumTokens.ACCENT_PRIMARY,
			0.20
		)

		menu_style.shadow_size = 10
	else:
		menu_style.shadow_color = Color.TRANSPARENT
		menu_style.shadow_size = 0

	hover_style = StyleBoxFlat.new()

	hover_style.bg_color = Color(
		StrontiumTokens.ACCENT_PRIMARY,
		0.14
	)

	hover_style.corner_radius_top_left = 5
	hover_style.corner_radius_top_right = 5
	hover_style.corner_radius_bottom_left = 5
	hover_style.corner_radius_bottom_right = 5

	hover_style.content_margin_left = 4
	hover_style.content_margin_top = 2
	hover_style.content_margin_right = 4
	hover_style.content_margin_bottom = 2


func _apply_styles() -> void:
	add_theme_stylebox_override(
		"panel",
		menu_style
	)

	add_theme_stylebox_override(
		"hover",
		hover_style
	)


func _on_id_pressed(
	id: int
) -> void:
	menu_action_selected.emit(
		id
	)


func append_menu_item(
	label: String,
	id: int,
	icon: Texture2D = null,
	disabled_state: bool = false
) -> void:
	add_item(
		label,
		id
	)

	var item_index := get_item_count() - 1

	if icon != null:
		set_item_icon(
			item_index,
			icon
		)

	set_item_disabled(
		item_index,
		disabled_state
	)


func append_menu_separator() -> void:
	add_separator()


func append_check_item(
	label: String,
	id: int,
	checked: bool = false
) -> void:
	add_check_item(
		label,
		id
	)

	var item_index := get_item_count() - 1

	set_item_checked(
		item_index,
		checked
	)


func set_menu_item_enabled(
	id: int,
	enabled: bool
) -> void:
	var index := get_item_index(id)

	if index < 0:
		return

	set_item_disabled(
		index,
		not enabled
	)


func set_menu_item_checked(
	id: int,
	checked: bool
) -> void:
	var index := get_item_index(id)

	if index < 0:
		return

	set_item_checked(
		index,
		checked
	)


func remove_menu_item(
	id: int
) -> void:
	var index := get_item_index(id)

	if index < 0:
		return

	remove_item(
		index
	)


func has_menu_item(
	id: int
) -> bool:
	return get_item_index(id) >= 0


func set_glow_enabled(
	enabled: bool
) -> void:
	glow_enabled = enabled

	_build_styles()
	_apply_styles()


func is_glow_enabled() -> bool:
	return glow_enabled


func set_menu_width(
	width: int
) -> void:
	menu_width = maxi(
		width,
		120
	)

	min_size = Vector2i(
		menu_width,
		0
	)


func get_menu_width() -> int:
	return menu_width


func refresh_style() -> void:
	_build_styles()
	_apply_styles()
