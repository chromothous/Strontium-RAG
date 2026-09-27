class_name StrontiumNavButton
extends Button


signal destination_selected(destination: String)
signal interaction_state_changed(state: InteractionState)


enum InteractionState {
	NORMAL,
	HOVER,
	PRESSED,
	ACTIVE,
	DISABLED
}


const BUTTON_HEIGHT := 44.0
const ACTIVE_INDICATOR_WIDTH := 3.0
const ACTIVE_INDICATOR_TOP := 4.0

const FOCUS_BORDER_WIDTH := 1

const BORDER_WIDTH_NORMAL := 1
const BORDER_WIDTH_PRESSED := 2

const GLOW_HOVER := 0.15
const GLOW_ACTIVE := 0.30
const GLOW_PRESSED := 0.50


var destination: String = ""

var active: bool = false
var hovered: bool = false
var pressed_state: bool = false
var focused: bool = false
var interaction_enabled: bool = true

var interaction_state: InteractionState = (
	InteractionState.NORMAL
)

var active_indicator: ColorRect
var focus_indicator: Panel

var indicator_tween: Tween
var focus_tween: Tween

var normal_style: StyleBoxFlat
var hover_style: StyleBoxFlat
var pressed_style: StyleBoxFlat
var focus_style: StyleBoxFlat
var disabled_style: StyleBoxFlat

var active_normal_style: StyleBoxFlat
var active_hover_style: StyleBoxFlat
var active_pressed_style: StyleBoxFlat


func _ready() -> void:
	_configure_control()
	_build_active_indicator()
	_build_focus_indicator()
	_build_styles()
	_connect_signals()
	_apply_state(false)


func setup(
	button_destination: String,
	button_text: String
) -> void:
	destination = button_destination
	text = button_text

	_configure_control()

	if not is_instance_valid(active_indicator):
		_build_active_indicator()

	if not is_instance_valid(focus_indicator):
		_build_focus_indicator()

	if normal_style == null:
		_build_styles()

	_connect_signals()
	_apply_state(false)


func _configure_control() -> void:
	custom_minimum_size = Vector2(
		0,
		BUTTON_HEIGHT
	)

	mouse_default_cursor_shape = (
		Control.CURSOR_POINTING_HAND
	)

	focus_mode = Control.FOCUS_ALL
	flat = false
	toggle_mode = false

	add_theme_font_size_override(
		"font_size",
		StrontiumTokens.FONT_SIZE_BODY
	)

	add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	add_theme_color_override(
		"font_hover_color",
		StrontiumTokens.ACCENT_PRIMARY
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
	if not pressed.is_connected(
		_on_pressed
	):
		pressed.connect(
			_on_pressed
		)

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

	if not focus_entered.is_connected(
		_on_focus_entered
	):
		focus_entered.connect(
			_on_focus_entered
		)

	if not focus_exited.is_connected(
		_on_focus_exited
	):
		focus_exited.connect(
			_on_focus_exited
		)


func _build_active_indicator() -> void:
	if is_instance_valid(active_indicator):
		return

	active_indicator = ColorRect.new()
	active_indicator.name = "ActiveIndicator"

	active_indicator.mouse_filter = (
		Control.MOUSE_FILTER_IGNORE
	)

	active_indicator.color = (
		StrontiumTokens.ACCENT_PRIMARY
	)

	active_indicator.anchor_left = 0.0
	active_indicator.anchor_top = 0.0
	active_indicator.anchor_right = 0.0
	active_indicator.anchor_bottom = 1.0

	active_indicator.offset_left = 0.0
	active_indicator.offset_top = (
		ACTIVE_INDICATOR_TOP
	)
	active_indicator.offset_right = (
		ACTIVE_INDICATOR_WIDTH
	)
	active_indicator.offset_bottom = (
		-ACTIVE_INDICATOR_TOP
	)

	add_child(active_indicator)

	move_child(
		active_indicator,
		get_child_count() - 1
	)

	active_indicator.modulate.a = 0.0


func _build_focus_indicator() -> void:
	if is_instance_valid(focus_indicator):
		return

	focus_indicator = Panel.new()
	focus_indicator.name = "FocusIndicator"

	focus_indicator.mouse_filter = (
		Control.MOUSE_FILTER_IGNORE
	)

	focus_indicator.set_anchors_and_offsets_preset(
		Control.PRESET_FULL_RECT
	)

	focus_indicator.offset_left = 1.0
	focus_indicator.offset_top = 1.0
	focus_indicator.offset_right = -1.0
	focus_indicator.offset_bottom = -1.0

	var focus_style := StyleBoxFlat.new()

	focus_style.bg_color = Color.TRANSPARENT
	focus_style.border_color = (
		StrontiumTokens.ACCENT_SECONDARY
	)

	focus_style.set_border_width(
		SIDE_LEFT,
		FOCUS_BORDER_WIDTH
	)

	focus_style.set_border_width(
		SIDE_TOP,
		FOCUS_BORDER_WIDTH
	)

	focus_style.set_border_width(
		SIDE_RIGHT,
		FOCUS_BORDER_WIDTH
	)

	focus_style.set_border_width(
		SIDE_BOTTOM,
		FOCUS_BORDER_WIDTH
	)

	focus_style.corner_radius_top_left = (
		StrontiumTokens.RADIUS_SMALL
	)

	focus_style.corner_radius_top_right = (
		StrontiumTokens.RADIUS_SMALL
	)

	focus_style.corner_radius_bottom_left = (
		StrontiumTokens.RADIUS_SMALL
	)

	focus_style.corner_radius_bottom_right = (
		StrontiumTokens.RADIUS_SMALL
	)

	focus_style.shadow_color = Color(
		StrontiumTokens.ACCENT_SECONDARY,
		0.40
	)

	focus_style.shadow_size = 6

	focus_indicator.add_theme_stylebox_override(
		"panel",
		focus_style
	)

	add_child(focus_indicator)

	move_child(
		focus_indicator,
		get_child_count() - 1
	)

	focus_indicator.modulate.a = 0.0


func _build_styles() -> void:
	normal_style = _create_style(
		StrontiumTokens.SURFACE_PRIMARY,
		StrontiumTokens.BORDER_SUBTLE,
		BORDER_WIDTH_NORMAL
	)

	hover_style = _create_style(
		StrontiumTokens.SURFACE_ELEVATED,
		StrontiumTokens.ACCENT_PRIMARY,
		BORDER_WIDTH_NORMAL
	)

	pressed_style = _create_style(
		StrontiumTokens.INTERACTION_ACTIVE,
		StrontiumTokens.ACCENT_PRIMARY,
		BORDER_WIDTH_PRESSED
	)

	focus_style = _create_style(
		StrontiumTokens.SURFACE_ELEVATED,
		StrontiumTokens.ACCENT_PRIMARY,
		BORDER_WIDTH_NORMAL
	)

	disabled_style = _create_style(
		StrontiumTokens.SURFACE_PRIMARY,
		StrontiumTokens.INTERACTION_DISABLED,
		BORDER_WIDTH_NORMAL
	)

	active_normal_style = _create_style(
		StrontiumTokens.SURFACE_ELEVATED,
		StrontiumTokens.BORDER_STANDARD,
		BORDER_WIDTH_NORMAL
	)

	active_hover_style = _create_style(
		StrontiumTokens.INTERACTION_HOVER,
		StrontiumTokens.ACCENT_PRIMARY,
		BORDER_WIDTH_NORMAL
	)

	active_pressed_style = _create_style(
		StrontiumTokens.INTERACTION_ACTIVE,
		StrontiumTokens.SPECTRUM_VIOLET,
		BORDER_WIDTH_PRESSED
	)

	_configure_glow(
		normal_style,
		Color.TRANSPARENT,
		0
	)

	_configure_glow(
		hover_style,
		Color(
			StrontiumTokens.ACCENT_PRIMARY,
			GLOW_HOVER
		),
		4
	)

	_configure_glow(
		pressed_style,
		Color(
			StrontiumTokens.ACCENT_PRIMARY,
			GLOW_ACTIVE
		),
		8
	)

	_configure_glow(
		focus_style,
		Color(
			StrontiumTokens.ACCENT_PRIMARY,
			GLOW_HOVER
		),
		5
	)

	_configure_glow(
		disabled_style,
		Color.TRANSPARENT,
		0
	)

	_configure_glow(
		active_normal_style,
		Color(
			StrontiumTokens.ACCENT_PRIMARY,
			0.12
		),
		3
	)

	_configure_glow(
		active_hover_style,
		Color(
			StrontiumTokens.ACCENT_PRIMARY,
			GLOW_ACTIVE
		),
		10
	)

	_configure_glow(
		active_pressed_style,
		Color(
			StrontiumTokens.SPECTRUM_VIOLET,
			GLOW_PRESSED
		),
		12
	)

	_apply_style_overrides()


func _configure_glow(
	style: StyleBoxFlat,
	color: Color,
	size: int
) -> void:
	style.shadow_color = color
	style.shadow_size = size


func _apply_style_overrides() -> void:
	add_theme_stylebox_override(
		"normal",
		normal_style
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
		focus_style
	)

	add_theme_stylebox_override(
		"disabled",
		disabled_style
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
		StrontiumTokens.RADIUS_SMALL
	)

	style.corner_radius_top_right = (
		StrontiumTokens.RADIUS_SMALL
	)

	style.corner_radius_bottom_left = (
		StrontiumTokens.RADIUS_SMALL
	)

	style.corner_radius_bottom_right = (
		StrontiumTokens.RADIUS_SMALL
	)

	style.content_margin_left = (
		StrontiumTokens.SPACE_XL
	)

	style.content_margin_right = (
		StrontiumTokens.SPACE_MD
	)

	style.content_margin_top = (
		StrontiumTokens.SPACE_SM
	)

	style.content_margin_bottom = (
		StrontiumTokens.SPACE_SM
	)

	return style


func _determine_state() -> InteractionState:
	if disabled or not interaction_enabled:
		return InteractionState.DISABLED

	if pressed_state:
		return InteractionState.PRESSED

	if active:
		return InteractionState.ACTIVE

	if hovered:
		return InteractionState.HOVER

	return InteractionState.NORMAL


func _apply_state(
	animated: bool = true
) -> void:
	var next_state := _determine_state()

	interaction_state = next_state

	_apply_state_visuals()
	_refresh_text_color()
	_apply_indicator(animated)
	_apply_focus_indicator(animated)

	interaction_state_changed.emit(
		interaction_state
	)


func _apply_state_visuals() -> void:
	match interaction_state:
		InteractionState.NORMAL:
			_apply_normal_styles()

		InteractionState.HOVER:
			_apply_hover_styles()

		InteractionState.PRESSED:
			_apply_pressed_styles()

		InteractionState.ACTIVE:
			_apply_active_styles()

		InteractionState.DISABLED:
			_apply_disabled_styles()


func _apply_normal_styles() -> void:
	add_theme_stylebox_override(
		"normal",
		normal_style
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
		focus_style
	)


func _apply_hover_styles() -> void:
	_apply_normal_styles()


func _apply_pressed_styles() -> void:
	add_theme_stylebox_override(
		"normal",
		pressed_style
	)

	add_theme_stylebox_override(
		"hover",
		pressed_style
	)

	add_theme_stylebox_override(
		"pressed",
		pressed_style
	)

	add_theme_stylebox_override(
		"focus",
		pressed_style
	)


func _apply_active_styles() -> void:
	add_theme_stylebox_override(
		"normal",
		active_normal_style
	)

	add_theme_stylebox_override(
		"hover",
		active_hover_style
	)

	add_theme_stylebox_override(
		"pressed",
		active_pressed_style
	)

	add_theme_stylebox_override(
		"focus",
		active_hover_style
	)


func _apply_disabled_styles() -> void:
	add_theme_stylebox_override(
		"normal",
		disabled_style
	)

	add_theme_stylebox_override(
		"hover",
		disabled_style
	)

	add_theme_stylebox_override(
		"pressed",
		disabled_style
	)

	add_theme_stylebox_override(
		"focus",
		disabled_style
	)


func _refresh_text_color() -> void:
	if disabled or not interaction_enabled:
		add_theme_color_override(
			"font_color",
			StrontiumTokens.INTERACTION_DISABLED
		)

		add_theme_color_override(
			"font_hover_color",
			StrontiumTokens.INTERACTION_DISABLED
		)

		return

	if active or pressed_state:
		add_theme_color_override(
			"font_color",
			StrontiumTokens.TEXT_PRIMARY
		)

		add_theme_color_override(
			"font_hover_color",
			StrontiumTokens.TEXT_PRIMARY
		)

		return

	if hovered:
		add_theme_color_override(
			"font_color",
			StrontiumTokens.ACCENT_PRIMARY
		)

		add_theme_color_override(
			"font_hover_color",
			StrontiumTokens.ACCENT_PRIMARY
		)

		return

	if focused:
		add_theme_color_override(
			"font_color",
			StrontiumTokens.TEXT_PRIMARY
		)

		add_theme_color_override(
			"font_hover_color",
			StrontiumTokens.ACCENT_PRIMARY
		)

		return

	add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	add_theme_color_override(
		"font_hover_color",
		StrontiumTokens.ACCENT_PRIMARY
	)


func _apply_indicator(
	animated: bool
) -> void:
	if not is_instance_valid(
		active_indicator
	):
		return

	_stop_indicator_tween()

	var target_alpha: float = 0.0

	var target_color := (
		StrontiumTokens.ACCENT_PRIMARY
	)

	if active and not disabled:
		target_alpha = 1.0

	if active and pressed_state:
		target_color = (
			StrontiumTokens.SPECTRUM_VIOLET
		)

	active_indicator.color = target_color

	if not animated:
		active_indicator.modulate.a = (
			target_alpha
		)
		return

	indicator_tween = create_tween()

	indicator_tween.set_trans(
		Tween.TRANS_QUAD
	)

	indicator_tween.set_ease(
		Tween.EASE_OUT
	)

	indicator_tween.tween_property(
		active_indicator,
		"modulate:a",
		target_alpha,
		StrontiumTokens.MOTION_STANDARD
	)


func _apply_focus_indicator(
	animated: bool
) -> void:
	if not is_instance_valid(
		focus_indicator
	):
		return

	_stop_focus_tween()

	var target_alpha: float = 0.0

	if (
		focused
		and not disabled
		and interaction_enabled
	):
		target_alpha = 1.0

	if not animated:
		focus_indicator.modulate.a = (
			target_alpha
		)
		return

	focus_tween = create_tween()

	focus_tween.set_trans(
		Tween.TRANS_QUAD
	)

	focus_tween.set_ease(
		Tween.EASE_OUT
	)

	focus_tween.tween_property(
		focus_indicator,
		"modulate:a",
		target_alpha,
		StrontiumTokens.MOTION_FAST
	)


func _stop_indicator_tween() -> void:
	if (
		indicator_tween != null
		and indicator_tween.is_valid()
	):
		indicator_tween.kill()

	indicator_tween = null


func _stop_focus_tween() -> void:
	if (
		focus_tween != null
		and focus_tween.is_valid()
	):
		focus_tween.kill()

	focus_tween = null


func _on_mouse_entered() -> void:
	if disabled or not interaction_enabled:
		return

	hovered = true

	_apply_state()


func _on_mouse_exited() -> void:
	hovered = false

	if disabled or not interaction_enabled:
		return

	_apply_state()


func _on_button_down() -> void:
	if disabled or not interaction_enabled:
		return

	pressed_state = true

	_apply_state()


func _on_button_up() -> void:
	if disabled or not interaction_enabled:
		return

	pressed_state = false

	_apply_state()


func _input(event: InputEvent) -> void:
	if not pressed_state:
		return

	if event is not InputEventMouseButton:
		return

	var mouse_event := (
		event as InputEventMouseButton
	)

	if mouse_event.button_index != MOUSE_BUTTON_LEFT:
		return

	if mouse_event.pressed:
		return

	pressed_state = false

	if disabled or not interaction_enabled:
		return

	_apply_state()


func _on_focus_entered() -> void:
	if disabled or not interaction_enabled:
		return

	focused = true

	_refresh_text_color()
	_apply_focus_indicator(true)


func _on_focus_exited() -> void:
	focused = false

	if disabled or not interaction_enabled:
		return

	_refresh_text_color()
	_apply_focus_indicator(true)


func _on_pressed() -> void:
	if disabled or not interaction_enabled:
		return

	destination_selected.emit(
		destination
	)


func set_active(
	value: bool
) -> void:
	if active == value:
		return

	active = value

	_apply_state()


func is_active() -> bool:
	return active


func set_interaction_enabled(
	value: bool
) -> void:
	interaction_enabled = value
	disabled = not value

	if not value:
		hovered = false
		pressed_state = false
		focused = false

	_apply_state()


func is_interaction_enabled() -> bool:
	return interaction_enabled


func set_disabled_state(
	value: bool
) -> void:
	disabled = value

	if value:
		hovered = false
		pressed_state = false
		focused = false

	_apply_state()


func is_disabled_state() -> bool:
	return (
		disabled
		or not interaction_enabled
	)


func get_interaction_state() -> InteractionState:
	return interaction_state


func get_interaction_state_name() -> String:
	return InteractionState.keys()[
		interaction_state
	]


func set_destination(
	value: String
) -> void:
	destination = value


func get_destination() -> String:
	return destination


func set_button_text(
	value: String
) -> void:
	text = value


func get_button_text() -> String:
	return text


func get_visual_state() -> Dictionary:
	return {
		"destination": destination,
		"text": text,
		"active": active,
		"hovered": hovered,
		"pressed": pressed_state,
		"focused": focused,
		"disabled": disabled,
		"interaction_enabled": interaction_enabled,
		"state": get_interaction_state_name()
	}


func _exit_tree() -> void:
	_stop_indicator_tween()
	_stop_focus_tween()
