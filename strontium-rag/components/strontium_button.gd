class_name StrontiumButton
extends Button


enum ButtonVariant {
	PRIMARY,
	SECONDARY,
	GHOST,
	DANGER
}


enum InteractionState {
	NORMAL,
	HOVER,
	PRESSED,
	DISABLED
}


@export var variant: ButtonVariant = ButtonVariant.PRIMARY
@export var glow_enabled: bool = true
@export var icon_enabled: bool = false


var interaction_state: InteractionState = (
	InteractionState.NORMAL
)

var hovered: bool = false
var pressed_state: bool = false

var base_style: StyleBoxFlat
var hover_style: StyleBoxFlat
var pressed_style: StyleBoxFlat
var disabled_style: StyleBoxFlat

var state_tween: Tween


func _ready() -> void:
	_configure_control()
	_build_styles()
	_connect_signals()
	_apply_state(false)


func _configure_control() -> void:
	custom_minimum_size = Vector2(
		120,
		40
	)

	mouse_default_cursor_shape = (
		Control.CURSOR_POINTING_HAND
	)

	focus_mode = Control.FOCUS_ALL
	flat = false

	add_theme_font_size_override(
		"font_size",
		StrontiumTokens.FONT_SIZE_BODY
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
		"font_focus_color",
		StrontiumTokens.TEXT_PRIMARY
	)

	add_theme_color_override(
		"font_disabled_color",
		StrontiumTokens.INTERACTION_DISABLED
	)

	add_theme_constant_override(
		"outline_size",
		0
	)


func _connect_signals() -> void:
	if not mouse_entered.is_connected(
		_on_mouse_entered
	):
		mouse_entered.connect(
			_on_mouse_entered
		)

	if not mouse_exited.is_connected(
		_on_mouse_exited
	):
		mouse_exited.connect(
			_on_mouse_exited
		)

	if not button_down.is_connected(
		_on_button_down
	):
		button_down.connect(
			_on_button_down
		)

	if not button_up.is_connected(
		_on_button_up
	):
		button_up.connect(
			_on_button_up
		)


func _build_styles() -> void:
	match variant:
		ButtonVariant.PRIMARY:
			_build_primary_styles()

		ButtonVariant.SECONDARY:
			_build_secondary_styles()

		ButtonVariant.GHOST:
			_build_ghost_styles()

		ButtonVariant.DANGER:
			_build_danger_styles()


func _build_primary_styles() -> void:
	base_style = _create_style(
		StrontiumTokens.SURFACE_ELEVATED,
		StrontiumTokens.ACCENT_PRIMARY,
		1
	)

	hover_style = _create_style(
		StrontiumTokens.INTERACTION_HOVER,
		StrontiumTokens.ACCENT_PRIMARY,
		2
	)

	pressed_style = _create_style(
		StrontiumTokens.INTERACTION_ACTIVE,
		StrontiumTokens.ACCENT_PRIMARY,
		2
	)

	disabled_style = _create_style(
		StrontiumTokens.SURFACE_PRIMARY,
		StrontiumTokens.INTERACTION_DISABLED,
		1
	)

	_configure_glow(
		base_style,
		StrontiumTokens.ACCENT_PRIMARY,
		0.15,
		5
	)

	_configure_glow(
		hover_style,
		StrontiumTokens.ACCENT_PRIMARY,
		0.35,
		10
	)

	_configure_glow(
		pressed_style,
		StrontiumTokens.ACCENT_PRIMARY,
		0.50,
		14
	)

	_configure_glow(
		disabled_style,
		Color.TRANSPARENT,
		0.0,
		0
	)

	add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_PRIMARY
	)


func _build_secondary_styles() -> void:
	base_style = _create_style(
		StrontiumTokens.SURFACE_PRIMARY,
		StrontiumTokens.BORDER_STANDARD,
		1
	)

	hover_style = _create_style(
		StrontiumTokens.SURFACE_ELEVATED,
		StrontiumTokens.ACCENT_PRIMARY,
		1
	)

	pressed_style = _create_style(
		StrontiumTokens.INTERACTION_ACTIVE,
		StrontiumTokens.ACCENT_PRIMARY,
		2
	)

	disabled_style = _create_style(
		StrontiumTokens.SURFACE_PRIMARY,
		StrontiumTokens.INTERACTION_DISABLED,
		1
	)

	_configure_glow(
		base_style,
		Color.TRANSPARENT,
		0.0,
		0
	)

	_configure_glow(
		hover_style,
		StrontiumTokens.ACCENT_PRIMARY,
		0.20,
		7
	)

	_configure_glow(
		pressed_style,
		StrontiumTokens.ACCENT_PRIMARY,
		0.35,
		10
	)

	_configure_glow(
		disabled_style,
		Color.TRANSPARENT,
		0.0,
		0
	)

	add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	add_theme_color_override(
		"font_hover_color",
		StrontiumTokens.ACCENT_PRIMARY
	)


func _build_ghost_styles() -> void:
	base_style = _create_style(
		Color.TRANSPARENT,
		Color.TRANSPARENT,
		1
	)

	hover_style = _create_style(
		StrontiumTokens.SURFACE_ELEVATED,
		StrontiumTokens.ACCENT_PRIMARY,
		1
	)

	pressed_style = _create_style(
		StrontiumTokens.INTERACTION_ACTIVE,
		StrontiumTokens.ACCENT_PRIMARY,
		1
	)

	disabled_style = _create_style(
		Color.TRANSPARENT,
		Color.TRANSPARENT,
		1
	)

	_configure_glow(
		base_style,
		Color.TRANSPARENT,
		0.0,
		0
	)

	_configure_glow(
		hover_style,
		StrontiumTokens.ACCENT_PRIMARY,
		0.15,
		6
	)

	_configure_glow(
		pressed_style,
		StrontiumTokens.ACCENT_PRIMARY,
		0.30,
		9
	)

	_configure_glow(
		disabled_style,
		Color.TRANSPARENT,
		0.0,
		0
	)

	add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	add_theme_color_override(
		"font_hover_color",
		StrontiumTokens.ACCENT_PRIMARY
	)


func _build_danger_styles() -> void:
	base_style = _create_style(
		StrontiumTokens.SURFACE_PRIMARY,
		StrontiumTokens.STATE_ERROR,
		1
	)

	hover_style = _create_style(
		StrontiumTokens.SURFACE_ELEVATED,
		StrontiumTokens.STATE_ERROR,
		2
	)

	pressed_style = _create_style(
		Color("#3A1D28"),
		StrontiumTokens.STATE_ERROR,
		2
	)

	disabled_style = _create_style(
		StrontiumTokens.SURFACE_PRIMARY,
		StrontiumTokens.INTERACTION_DISABLED,
		1
	)

	_configure_glow(
		base_style,
		StrontiumTokens.STATE_ERROR,
		0.12,
		4
	)

	_configure_glow(
		hover_style,
		StrontiumTokens.STATE_ERROR,
		0.30,
		9
	)

	_configure_glow(
		pressed_style,
		StrontiumTokens.STATE_ERROR,
		0.45,
		13
	)

	_configure_glow(
		disabled_style,
		Color.TRANSPARENT,
		0.0,
		0
	)

	add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_PRIMARY
	)

	add_theme_color_override(
		"font_hover_color",
		StrontiumTokens.TEXT_PRIMARY
	)


func _create_style(
	background: Color,
	border: Color,
	border_width: int
) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()

	style.bg_color = background
	style.border_color = border

	style.set_border_width(
		SIDE_LEFT,
		border_width
	)

	style.set_border_width(
		SIDE_TOP,
		border_width
	)

	style.set_border_width(
		SIDE_RIGHT,
		border_width
	)

	style.set_border_width(
		SIDE_BOTTOM,
		border_width
	)

	style.corner_radius_top_left = (
		StrontiumTokens.RADIUS_STANDARD
	)

	style.corner_radius_top_right = (
		StrontiumTokens.RADIUS_STANDARD
	)

	style.corner_radius_bottom_left = (
		StrontiumTokens.RADIUS_STANDARD
	)

	style.corner_radius_bottom_right = (
		StrontiumTokens.RADIUS_STANDARD
	)

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

	return style


func _configure_glow(
	style: StyleBoxFlat,
	color: Color,
	alpha: float,
	size: int
) -> void:
	if not glow_enabled:
		style.shadow_color = Color.TRANSPARENT
		style.shadow_size = 0
		return

	style.shadow_color = Color(
		color,
		alpha
	)

	style.shadow_size = size


func _apply_state(
	animated: bool = true
) -> void:
	if disabled:
		interaction_state = (
			InteractionState.DISABLED
		)
	elif pressed_state:
		interaction_state = (
			InteractionState.PRESSED
		)
	elif hovered:
		interaction_state = (
			InteractionState.HOVER
		)
	else:
		interaction_state = (
			InteractionState.NORMAL
		)

	_refresh_style_overrides()

	if animated:
		_animate_state_change()


func _refresh_style_overrides() -> void:
	add_theme_stylebox_override(
		"normal",
		base_style
	)

	add_theme_stylebox_override(
		"hover",
		hover_style
	)

	add_theme_stylebox_override(
		"pressed",
		pressed_style
	)

	add_theme_stylebox_override(
		"focus",
		hover_style
	)

	add_theme_stylebox_override(
		"disabled",
		disabled_style
	)


func _animate_state_change() -> void:
	_stop_state_tween()

	if not is_instance_valid(
		hover_style
	):
		return

	var target_scale := Vector2.ONE

	match interaction_state:
		InteractionState.NORMAL:
			target_scale = Vector2.ONE

		InteractionState.HOVER:
			target_scale = Vector2(
				1.01,
				1.01
			)

		InteractionState.PRESSED:
			target_scale = Vector2(
				0.985,
				0.985
			)

		InteractionState.DISABLED:
			target_scale = Vector2.ONE

	state_tween = create_tween()

	state_tween.set_trans(
		Tween.TRANS_QUAD
	)

	state_tween.set_ease(
		Tween.EASE_OUT
	)

	state_tween.tween_property(
		self,
		"scale",
		target_scale,
		StrontiumTokens.MOTION_FAST
	)


func _stop_state_tween() -> void:
	if (
		state_tween != null
		and state_tween.is_valid()
	):
		state_tween.kill()

	state_tween = null


func _on_mouse_entered() -> void:
	if disabled:
		return

	hovered = true
	_apply_state()


func _on_mouse_exited() -> void:
	hovered = false

	if disabled:
		return

	_apply_state()


func _on_button_down() -> void:
	if disabled:
		return

	pressed_state = true
	_apply_state()


func _on_button_up() -> void:
	if disabled:
		return

	pressed_state = false
	_apply_state()


func set_variant(
	new_variant: ButtonVariant
) -> void:
	variant = new_variant

	_stop_state_tween()
	_build_styles()
	_apply_state(false)


func get_variant() -> ButtonVariant:
	return variant


func set_glow_enabled(
	enabled: bool
) -> void:
	glow_enabled = enabled

	_stop_state_tween()
	_build_styles()
	_apply_state(false)


func is_glow_enabled() -> bool:
	return glow_enabled


func set_button_text(
	value: String
) -> void:
	text = value


func get_button_text() -> String:
	return text


func set_interaction_enabled(
	enabled: bool
) -> void:
	disabled = not enabled

	if not enabled:
		hovered = false
		pressed_state = false

	_apply_state(false)


func is_interaction_enabled() -> bool:
	return not disabled


func get_interaction_state() -> InteractionState:
	return interaction_state


func get_interaction_state_name() -> String:
	return InteractionState.keys()[
		interaction_state
	]


func _exit_tree() -> void:
	_stop_state_tween()
