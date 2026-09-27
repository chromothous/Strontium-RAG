class_name StrontiumProgressIndicator
extends ProgressBar


enum ProgressVariant {
	STANDARD,
	ACCENT,
	SUCCESS,
	WARNING,
	ERROR
}


@export var variant: ProgressVariant = ProgressVariant.STANDARD
@export var glow_enabled: bool = true
@export var percentage_visible: bool = false
@export var bar_height: float = 6.0
@export var corner_radius: int = 3


var background_style: StyleBoxFlat
var fill_style: StyleBoxFlat


func _ready() -> void:
	_configure_control()
	_build_styles()
	_apply_styles()


func _configure_control() -> void:
	custom_minimum_size = Vector2(
		180.0,
		bar_height + 8.0
	)

	show_percentage = percentage_visible

	add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)


func _build_styles() -> void:
	var accent_color := _get_accent_color()

	background_style = _create_background_style()

	fill_style = _create_fill_style(
		accent_color
	)

	if glow_enabled:
		fill_style.shadow_color = Color(
			accent_color,
			0.35
		)

		fill_style.shadow_size = 8
	else:
		fill_style.shadow_color = Color.TRANSPARENT
		fill_style.shadow_size = 0


func _create_background_style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()

	style.bg_color = StrontiumTokens.BORDER_STANDARD.darkened(
		0.35
	)

	style.corner_radius_top_left = corner_radius
	style.corner_radius_top_right = corner_radius
	style.corner_radius_bottom_left = corner_radius
	style.corner_radius_bottom_right = corner_radius

	return style


func _create_fill_style(
	accent_color: Color
) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()

	style.bg_color = accent_color

	style.corner_radius_top_left = corner_radius
	style.corner_radius_top_right = corner_radius
	style.corner_radius_bottom_left = corner_radius
	style.corner_radius_bottom_right = corner_radius

	return style


func _apply_styles() -> void:
	add_theme_stylebox_override(
		"background",
		background_style
	)

	add_theme_stylebox_override(
		"fill",
		fill_style
	)


func _get_accent_color() -> Color:
	match variant:
		ProgressVariant.STANDARD:
			return StrontiumTokens.ACCENT_PRIMARY

		ProgressVariant.ACCENT:
			return StrontiumTokens.SPECTRUM_VIOLET

		ProgressVariant.SUCCESS:
			return StrontiumTokens.STATE_SUCCESS

		ProgressVariant.WARNING:
			return StrontiumTokens.STATE_WARNING

		ProgressVariant.ERROR:
			return StrontiumTokens.STATE_ERROR

	return StrontiumTokens.ACCENT_PRIMARY


func set_variant(
	new_variant: ProgressVariant
) -> void:
	variant = new_variant

	_build_styles()
	_apply_styles()


func get_variant() -> ProgressVariant:
	return variant


func set_glow_enabled(
	enabled: bool
) -> void:
	glow_enabled = enabled

	_build_styles()
	_apply_styles()


func is_glow_enabled() -> bool:
	return glow_enabled


func set_percentage_visible(
	visible: bool
) -> void:
	percentage_visible = visible
	show_percentage = visible


func is_percentage_visible() -> bool:
	return show_percentage


func set_bar_height(
	height: float
) -> void:
	bar_height = maxf(
		height,
		1.0
	)

	custom_minimum_size = Vector2(
		custom_minimum_size.x,
		bar_height + 8.0
	)

	_build_styles()
	_apply_styles()


func get_bar_height() -> float:
	return bar_height


func set_corner_radius(
	radius: int
) -> void:
	corner_radius = maxi(
		radius,
		0
	)

	_build_styles()
	_apply_styles()


func get_corner_radius() -> int:
	return corner_radius


func set_progress_range(
	minimum: float,
	maximum: float
) -> void:
	min_value = minimum
	max_value = maximum

	value = clampf(
		value,
		min_value,
		max_value
	)


func set_progress_value(
	new_value: float
) -> void:
	value = clampf(
		new_value,
		min_value,
		max_value
	)


func get_progress_value() -> float:
	return value


func get_progress_ratio() -> float:
	if is_equal_approx(
		max_value,
		min_value
	):
		return 0.0

	return clampf(
		inverse_lerp(
			min_value,
			max_value,
			value
		),
		0.0,
		1.0
	)


func set_indeterminate_mode(
	enabled: bool
) -> void:
	indeterminate = enabled


func is_indeterminate_mode() -> bool:
	return indeterminate


func configure_progress(
	minimum: float,
	maximum: float,
	start_value: float = 0.0,
	show_percent: bool = false
) -> void:
	min_value = minimum
	max_value = maximum

	value = clampf(
		start_value,
		minimum,
		maximum
	)

	percentage_visible = show_percent
	show_percentage = show_percent


func refresh_style() -> void:
	_build_styles()
	_apply_styles()
