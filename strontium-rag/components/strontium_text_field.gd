class_name StrontiumTextField
extends LineEdit


enum FieldVariant {
	STANDARD,
	SEARCH,
	SECRET,
	MULTILINE_LIKE
}


enum ValidationState {
	NONE,
	VALID,
	WARNING,
	ERROR
}


signal validation_state_changed(
	state: ValidationState
)

signal submitted_value(
	value: String
)


@export var variant: FieldVariant = FieldVariant.STANDARD
@export var validation_state: ValidationState = (
	ValidationState.NONE
)

@export var validation_message: String = ""
@export var field_clear_button: bool = true
@export var glow_enabled: bool = true
@export var field_select_all_on_focus: bool = false


var normal_style: StyleBoxFlat
var focus_style: StyleBoxFlat
var warning_style: StyleBoxFlat
var error_style: StyleBoxFlat
var valid_style: StyleBoxFlat


func _ready() -> void:
	_configure_control()
	_build_styles()
	_connect_signals()
	_apply_variant()
	_apply_validation_state()


func _configure_control() -> void:
	custom_minimum_size = Vector2(
		240,
		40
	)

	mouse_default_cursor_shape = (
		Control.CURSOR_IBEAM
	)

	focus_mode = Control.FOCUS_ALL

	clear_button_enabled = (
		field_clear_button
	)

	select_all_on_focus = (
		field_select_all_on_focus
	)

	add_theme_font_size_override(
		"font_size",
		StrontiumTokens.FONT_SIZE_BODY
	)

	add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_PRIMARY
	)

	add_theme_color_override(
		"font_placeholder_color",
		StrontiumTokens.TEXT_MUTED
	)

	add_theme_color_override(
		"caret_color",
		StrontiumTokens.ACCENT_PRIMARY
	)

	add_theme_color_override(
		"selection_color",
		Color(
			StrontiumTokens.ACCENT_PRIMARY,
			0.25
		)
	)

	add_theme_color_override(
		"font_uneditable_color",
		StrontiumTokens.TEXT_MUTED
	)

	add_theme_constant_override(
		"minimum_character_width",
		0
	)


func _connect_signals() -> void:
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

	if not text_submitted.is_connected(
		_on_text_submitted
	):
		text_submitted.connect(
			_on_text_submitted
		)


func _build_styles() -> void:
	normal_style = _create_style(
		StrontiumTokens.SURFACE_PRIMARY,
		StrontiumTokens.BORDER_SUBTLE
	)

	focus_style = _create_style(
		StrontiumTokens.SURFACE_ELEVATED,
		StrontiumTokens.ACCENT_PRIMARY
	)

	valid_style = _create_style(
		StrontiumTokens.SURFACE_PRIMARY,
		StrontiumTokens.STATE_SUCCESS
	)

	warning_style = _create_style(
		StrontiumTokens.SURFACE_PRIMARY,
		StrontiumTokens.STATE_WARNING
	)

	error_style = _create_style(
		StrontiumTokens.SURFACE_PRIMARY,
		StrontiumTokens.STATE_ERROR
	)

	_configure_style_glow(
		normal_style,
		Color.TRANSPARENT,
		0.0,
		0
	)

	_configure_style_glow(
		focus_style,
		StrontiumTokens.ACCENT_PRIMARY,
		0.25,
		8
	)

	_configure_style_glow(
		valid_style,
		StrontiumTokens.STATE_SUCCESS,
		0.18,
		6
	)

	_configure_style_glow(
		warning_style,
		StrontiumTokens.STATE_WARNING,
		0.22,
		7
	)

	_configure_style_glow(
		error_style,
		StrontiumTokens.STATE_ERROR,
		0.28,
		9
	)

	add_theme_stylebox_override(
		"normal",
		normal_style
	)

	add_theme_stylebox_override(
		"focus",
		focus_style
	)


func _create_style(
	background: Color,
	border: Color
) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()

	style.bg_color = background
	style.border_color = border

	style.set_border_width(
		SIDE_LEFT,
		StrontiumTokens.BORDER_WIDTH_STANDARD
	)

	style.set_border_width(
		SIDE_TOP,
		StrontiumTokens.BORDER_WIDTH_STANDARD
	)

	style.set_border_width(
		SIDE_RIGHT,
		StrontiumTokens.BORDER_WIDTH_STANDARD
	)

	style.set_border_width(
		SIDE_BOTTOM,
		StrontiumTokens.BORDER_WIDTH_STANDARD
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
		StrontiumTokens.SPACE_MD
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


func _configure_style_glow(
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


func _apply_variant() -> void:
	match variant:
		FieldVariant.STANDARD:
			clear_button_enabled = (
				field_clear_button
			)

		FieldVariant.SEARCH:
			clear_button_enabled = true

		FieldVariant.SECRET:
			secret = true

			clear_button_enabled = (
				field_clear_button
			)

		FieldVariant.MULTILINE_LIKE:
			clear_button_enabled = (
				field_clear_button
			)


func _apply_validation_state() -> void:
	match validation_state:
		ValidationState.NONE:
			_apply_normal_validation_style()

		ValidationState.VALID:
			_apply_valid_style()

		ValidationState.WARNING:
			_apply_warning_style()

		ValidationState.ERROR:
			_apply_error_style()


func _apply_normal_validation_style() -> void:
	add_theme_stylebox_override(
		"normal",
		normal_style
	)

	add_theme_stylebox_override(
		"focus",
		focus_style
	)


func _apply_valid_style() -> void:
	add_theme_stylebox_override(
		"normal",
		valid_style
	)

	if has_focus():
		add_theme_stylebox_override(
			"focus",
			valid_style
		)
	else:
		add_theme_stylebox_override(
			"focus",
			focus_style
		)


func _apply_warning_style() -> void:
	add_theme_stylebox_override(
		"normal",
		warning_style
	)

	if has_focus():
		add_theme_stylebox_override(
			"focus",
			warning_style
		)
	else:
		add_theme_stylebox_override(
			"focus",
			focus_style
		)


func _apply_error_style() -> void:
	add_theme_stylebox_override(
		"normal",
		error_style
	)

	if has_focus():
		add_theme_stylebox_override(
			"focus",
			error_style
		)
	else:
		add_theme_stylebox_override(
			"focus",
			focus_style
		)


func _on_focus_entered() -> void:
	if field_select_all_on_focus:
		select_all()

	match validation_state:
		ValidationState.NONE:
			add_theme_stylebox_override(
				"focus",
				focus_style
			)

		ValidationState.VALID:
			add_theme_stylebox_override(
				"focus",
				valid_style
			)

		ValidationState.WARNING:
			add_theme_stylebox_override(
				"focus",
				warning_style
			)

		ValidationState.ERROR:
			add_theme_stylebox_override(
				"focus",
				error_style
			)


func _on_focus_exited() -> void:
	_apply_validation_state()


func _on_text_submitted(
	value: String
) -> void:
	submitted_value.emit(
		value
	)


func set_variant(
	new_variant: FieldVariant
) -> void:
	variant = new_variant

	if variant == FieldVariant.SECRET:
		secret = true
	else:
		secret = false

	_apply_variant()


func get_variant() -> FieldVariant:
	return variant


func set_validation_state(
	new_state: ValidationState,
	message: String = ""
) -> void:
	validation_state = new_state
	validation_message = message

	_apply_validation_state()

	validation_state_changed.emit(
		validation_state
	)


func get_validation_state() -> ValidationState:
	return validation_state


func get_validation_state_name() -> String:
	return ValidationState.keys()[
		validation_state
	]


func get_validation_message() -> String:
	return validation_message


func set_field_clear_button_enabled(
	enabled: bool
) -> void:
	field_clear_button = enabled
	clear_button_enabled = enabled


func is_field_clear_button_enabled() -> bool:
	return field_clear_button


func set_field_select_all_on_focus(
	enabled: bool
) -> void:
	field_select_all_on_focus = enabled
	select_all_on_focus = enabled


func is_field_select_all_on_focus() -> bool:
	return field_select_all_on_focus


func set_glow_enabled(
	enabled: bool
) -> void:
	glow_enabled = enabled

	if not glow_enabled:
		_configure_style_glow(
			focus_style,
			Color.TRANSPARENT,
			0.0,
			0
		)

		_configure_style_glow(
			valid_style,
			Color.TRANSPARENT,
			0.0,
			0
		)

		_configure_style_glow(
			warning_style,
			Color.TRANSPARENT,
			0.0,
			0
		)

		_configure_style_glow(
			error_style,
			Color.TRANSPARENT,
			0.0,
			0
		)
	else:
		_configure_style_glow(
			focus_style,
			StrontiumTokens.ACCENT_PRIMARY,
			0.25,
			8
		)

		_configure_style_glow(
			valid_style,
			StrontiumTokens.STATE_SUCCESS,
			0.18,
			6
		)

		_configure_style_glow(
			warning_style,
			StrontiumTokens.STATE_WARNING,
			0.22,
			7
		)

		_configure_style_glow(
			error_style,
			StrontiumTokens.STATE_ERROR,
			0.28,
			9
		)

	_apply_validation_state()


func refresh_style() -> void:
	_build_styles()
	_apply_validation_state()


func is_valid_input() -> bool:
	return validation_state == ValidationState.VALID


func has_warning() -> bool:
	return validation_state == ValidationState.WARNING


func has_error() -> bool:
	return validation_state == ValidationState.ERROR
