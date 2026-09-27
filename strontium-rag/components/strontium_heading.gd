class_name StrontiumHeading
extends Label


enum HeadingLevel {
	SMALL,
	STANDARD,
	LARGE,
	DISPLAY
}


enum HeadingTone {
	PRIMARY,
	SECONDARY,
	MUTED,
	ACCENT
}


@export var level: HeadingLevel = HeadingLevel.STANDARD
@export var tone: HeadingTone = HeadingTone.PRIMARY
@export var use_uppercase: bool = false
@export var glow_enabled: bool = false
@export var glow_strength: float = 0.20
@export var shadow_enabled: bool = false


func _ready() -> void:
	_apply_heading_style()


func _apply_heading_style() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE

	horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	vertical_alignment = VERTICAL_ALIGNMENT_CENTER

	autowrap_mode = TextServer.AUTOWRAP_OFF

	var font_size: int = (
		StrontiumTokens.FONT_SIZE_HEADING
	)

	match level:
		HeadingLevel.SMALL:
			font_size = (
				StrontiumTokens.FONT_SIZE_HEADING_SMALL
			)

		HeadingLevel.STANDARD:
			font_size = (
				StrontiumTokens.FONT_SIZE_HEADING
			)

		HeadingLevel.LARGE:
			font_size = (
				StrontiumTokens.FONT_SIZE_HEADING_LARGE
			)

		HeadingLevel.DISPLAY:
			font_size = (
				StrontiumTokens.FONT_SIZE_DISPLAY
			)

	add_theme_font_size_override(
		"font_size",
		font_size
	)

	var heading_color := _get_heading_color()

	add_theme_color_override(
		"font_color",
		heading_color
	)

	if glow_enabled:
		add_theme_color_override(
			"font_shadow_color",
			Color(
				heading_color,
				clampf(
					glow_strength,
					0.0,
					1.0
				)
			)
		)

		add_theme_constant_override(
			"shadow_offset_x",
			0
		)

		add_theme_constant_override(
			"shadow_offset_y",
			0
		)

		add_theme_constant_override(
			"shadow_outline_size",
			4
		)
	else:
		add_theme_color_override(
			"font_shadow_color",
			Color.TRANSPARENT
		)

		add_theme_constant_override(
			"shadow_offset_x",
			0
		)

		add_theme_constant_override(
			"shadow_offset_y",
			0
		)

		add_theme_constant_override(
			"shadow_outline_size",
			0
		)

	if shadow_enabled:
		add_theme_constant_override(
			"shadow_offset_x",
			2
		)

		add_theme_constant_override(
			"shadow_offset_y",
			2
		)

		add_theme_constant_override(
			"shadow_outline_size",
			1
		)

	if use_uppercase:
		text = text.to_upper()


func _get_heading_color() -> Color:
	match tone:
		HeadingTone.PRIMARY:
			return StrontiumTokens.TEXT_PRIMARY

		HeadingTone.SECONDARY:
			return StrontiumTokens.TEXT_SECONDARY

		HeadingTone.MUTED:
			return StrontiumTokens.TEXT_MUTED

		HeadingTone.ACCENT:
			return StrontiumTokens.ACCENT_PRIMARY

	return StrontiumTokens.TEXT_PRIMARY


func set_level(
	new_level: HeadingLevel
) -> void:
	level = new_level
	_apply_heading_style()


func get_level() -> HeadingLevel:
	return level


func set_tone(
	new_tone: HeadingTone
) -> void:
	tone = new_tone
	_apply_heading_style()


func get_tone() -> HeadingTone:
	return tone


func set_heading_uppercase(
	value: bool
) -> void:
	use_uppercase = value
	_apply_heading_style()


func is_heading_uppercase() -> bool:
	return use_uppercase


func set_glow(
	enabled: bool,
	strength: float = 0.20
) -> void:
	glow_enabled = enabled
	glow_strength = strength
	_apply_heading_style()


func set_shadow(
	enabled: bool
) -> void:
	shadow_enabled = enabled
	_apply_heading_style()


func refresh_style() -> void:
	_apply_heading_style()
