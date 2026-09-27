class_name StrontiumSlider
extends HSlider


enum SliderVariant {
	STANDARD,
	ACCENT,
	WARNING,
	ERROR
}


signal slider_value_changed(value: float)
signal interaction_state_changed(state: InteractionState)


enum InteractionState {
	NORMAL,
	HOVER,
	DISABLED
}


@export var variant: SliderVariant = SliderVariant.STANDARD
@export var glow_enabled: bool = true
@export var show_ticks: bool = false
@export var track_height: float = 4.0
@export var grabber_size: float = 14.0


var interaction_state: InteractionState = (
	InteractionState.NORMAL
)

var hovered: bool = false
var interaction_enabled: bool = true

var slider_style: StyleBoxFlat
var slider_highlight_style: StyleBoxFlat
var grabber_style: StyleBoxFlat
var grabber_highlight_style: StyleBoxFlat
var disabled_style: StyleBoxFlat


func _ready() -> void:
	_configure_control()
	_build_styles()
	_connect_signals()
	_apply_state()


func _configure_control() -> void:
	custom_minimum_size = Vector2(
		180,
		24
	)

	mouse_default_cursor_shape = (
		Control.CURSOR_POINTING_HAND
	)

	focus_mode = Control.FOCUS_ALL

	tick_count = 0
	ticks_on_borders = false

	add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	add_theme_color_override(
		"font_disabled_color",
		StrontiumTokens.INTERACTION_DISABLED
	)


func _build_styles() -> void:
	var accent_color := _get_accent_color()

	slider_style = _create_track_style(
		StrontiumTokens.BORDER_STANDARD
	)

	slider_highlight_style = _create_track_style(
		accent_color
	)

	grabber_style = _create_grabber_style(
		accent_color,
		false
	)

	grabber_highlight_style = _create_grabber_style(
		accent_color,
		true
	)

	disabled_style = _create_track_style(
		StrontiumTokens.INTERACTION_DISABLED
	)

	_configure_track_glow(
		slider_highlight_style,
		accent_color,
		0.18,
		5
	)

	if glow_enabled:
		_configure_grabber_glow(
			grabber_highlight_style,
			accent_color
		)
	else:
		_configure_grabber_glow(
			grabber_highlight_style,
			Color.TRANSPARENT
		)

	add_theme_stylebox_override(
		"slider",
		slider_style
	)

	add_theme_stylebox_override(
		"grabber",
		grabber_style
	)

	add_theme_stylebox_override(
		"grabber_highlight",
		grabber_highlight_style
	)


func _create_track_style(
	color: Color
) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()

	style.bg_color = color

	style.corner_radius_top_left = 3
	style.corner_radius_top_right = 3
	style.corner_radius_bottom_left = 3
	style.corner_radius_bottom_right = 3

	style.content_margin_top = (
		track_height / 2.0
	)

	style.content_margin_bottom = (
		track_height / 2.0
	)

	return style


func _create_grabber_style(
	color: Color,
	highlighted: bool
) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()

	style.bg_color = color

	var radius := int(
		grabber_size / 2.0
	)

	style.corner_radius_top_left = radius
	style.corner_radius_top_right = radius
	style.corner_radius_bottom_left = radius
	style.corner_radius_bottom_right = radius

	style.content_margin_left = (
		grabber_size / 2.0
	)

	style.content_margin_right = (
		grabber_size / 2.0
	)

	style.content_margin_top = (
		grabber_size / 2.0
	)

	style.content_margin_bottom = (
		grabber_size / 2.0
	)

	if highlighted:
		style.bg_color = color.lightened(
			0.08
		)

	return style


func _configure_track_glow(
	style: StyleBoxFlat,
	color: Color,
	alpha: float,
	size: int
) -> void:
	style.shadow_color = Color(
		color,
		alpha
	)

	style.shadow_size = size


func _configure_grabber_glow(
	style: StyleBoxFlat,
	color: Color
) -> void:
	if color == Color.TRANSPARENT:
		style.shadow_color = Color.TRANSPARENT
		style.shadow_size = 0
		return

	style.shadow_color = Color(
		color,
		0.45
	)

	style.shadow_size = 8


func _get_accent_color() -> Color:
	match variant:
		SliderVariant.STANDARD:
			return StrontiumTokens.ACCENT_PRIMARY

		SliderVariant.ACCENT:
			return StrontiumTokens.SPECTRUM_VIOLET

		SliderVariant.WARNING:
			return StrontiumTokens.STATE_WARNING

		SliderVariant.ERROR:
			return StrontiumTokens.STATE_ERROR

	return StrontiumTokens.ACCENT_PRIMARY


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

	if not value_changed.is_connected(
		_on_value_changed
	):
		value_changed.connect(
			_on_value_changed
		)


func _on_mouse_entered() -> void:
	if not interaction_enabled:
		return

	hovered = true
	_apply_state()


func _on_mouse_exited() -> void:
	hovered = false

	if not interaction_enabled:
		return

	_apply_state()


func _on_value_changed(
	new_value: float
) -> void:
	slider_value_changed.emit(
		new_value
	)


func _apply_state() -> void:
	if not interaction_enabled:
		interaction_state = (
			InteractionState.DISABLED
		)

	elif hovered:
		interaction_state = (
			InteractionState.HOVER
		)

	else:
		interaction_state = (
			InteractionState.NORMAL
		)

	_apply_state_visuals()

	interaction_state_changed.emit(
		interaction_state
	)


func _apply_state_visuals() -> void:
	if not interaction_enabled:
		add_theme_stylebox_override(
			"slider",
			disabled_style
		)

		add_theme_stylebox_override(
			"grabber",
			disabled_style
		)

		add_theme_stylebox_override(
			"grabber_highlight",
			disabled_style
		)

		add_theme_color_override(
			"font_color",
			StrontiumTokens.INTERACTION_DISABLED
		)

		mouse_default_cursor_shape = (
			Control.CURSOR_ARROW
		)

		return

	add_theme_stylebox_override(
		"slider",
		slider_style
	)

	if hovered:
		add_theme_stylebox_override(
			"grabber",
			grabber_highlight_style
		)

		add_theme_stylebox_override(
			"grabber_highlight",
			grabber_highlight_style
		)
	else:
		add_theme_stylebox_override(
			"grabber",
			grabber_style
		)

		add_theme_stylebox_override(
			"grabber_highlight",
			grabber_highlight_style
		)

	add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	mouse_default_cursor_shape = (
		Control.CURSOR_POINTING_HAND
	)


func set_variant(
	new_variant: SliderVariant
) -> void:
	variant = new_variant

	_build_styles()
	_apply_state()


func get_variant() -> SliderVariant:
	return variant


func set_glow_enabled(
	enabled: bool
) -> void:
	glow_enabled = enabled

	_build_styles()
	_apply_state()


func is_glow_enabled() -> bool:
	return glow_enabled


func set_track_height(
	height: float
) -> void:
	track_height = maxf(
		height,
		1.0
	)

	_build_styles()
	_apply_state()


func get_track_height() -> float:
	return track_height


func set_grabber_size(
	size: float
) -> void:
	grabber_size = maxf(
		size,
		4.0
	)

	_build_styles()
	_apply_state()


func get_grabber_size() -> float:
	return grabber_size


func set_ticks_visible(
	visible: bool
) -> void:
	show_ticks = visible

	if show_ticks:
		tick_count = 5
	else:
		tick_count = 0


func are_ticks_visible() -> bool:
	return show_ticks


func set_slider_range(
	minimum: float,
	maximum: float,
	step_size: float = 0.0
) -> void:
	min_value = minimum
	max_value = maximum
	step = step_size


func set_slider_value(
	new_value: float
) -> void:
	value = clampf(
		new_value,
		min_value,
		max_value
	)


func get_slider_value() -> float:
	return value


func set_interaction_enabled(
	enabled: bool
) -> void:
	interaction_enabled = enabled
	hovered = false

	_apply_state()


func is_interaction_enabled() -> bool:
	return interaction_enabled


func get_interaction_state() -> InteractionState:
	return interaction_state


func get_interaction_state_name() -> String:
	return InteractionState.keys()[
		interaction_state
	]


func refresh_style() -> void:
	_build_styles()
	_apply_state()
