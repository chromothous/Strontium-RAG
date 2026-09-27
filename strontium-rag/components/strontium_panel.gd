class_name StrontiumPanel
extends PanelContainer


enum PanelVariant {
	PRIMARY,
	SECONDARY,
	ELEVATED,
	OUTLINE,
	ACTIVE,
	WARNING,
	ERROR
}


@export var variant: PanelVariant = PanelVariant.PRIMARY
@export var padding: int = StrontiumTokens.SPACE_LG
@export var glow_enabled: bool = false
@export var interactive: bool = false


var current_style: StyleBoxFlat
var hover_style: StyleBoxFlat

var hovered: bool = false
var transition_tween: Tween


func _ready() -> void:
	_configure_control()
	_build_styles()
	_connect_signals()
	_apply_state(false)


func _configure_control() -> void:
	mouse_filter = (
		Control.MOUSE_FILTER_STOP
		if interactive
		else Control.MOUSE_FILTER_IGNORE
	)

	add_theme_constant_override(
		"margin_left",
		padding
	)

	add_theme_constant_override(
		"margin_top",
		padding
	)

	add_theme_constant_override(
		"margin_right",
		padding
	)

	add_theme_constant_override(
		"margin_bottom",
		padding
	)


func _build_styles() -> void:
	var colors := _get_variant_colors()

	current_style = _create_style(
		colors["background"],
		colors["border"]
	)

	hover_style = _create_style(
		colors["hover_background"],
		colors["hover_border"]
	)

	if glow_enabled:
		_configure_glow(
			current_style,
			colors["glow_color"],
			colors["glow_alpha"],
			colors["glow_size"]
		)

		_configure_glow(
			hover_style,
			colors["glow_color"],
			colors["hover_glow_alpha"],
			colors["hover_glow_size"]
		)
	else:
		_configure_glow(
			current_style,
			Color.TRANSPARENT,
			0.0,
			0
		)

		_configure_glow(
			hover_style,
			Color.TRANSPARENT,
			0.0,
			0
		)


func _get_variant_colors() -> Dictionary:
	match variant:
		PanelVariant.PRIMARY:
			return {
				"background": StrontiumTokens.SURFACE_PRIMARY,
				"border": StrontiumTokens.BORDER_SUBTLE,
				"hover_background": StrontiumTokens.SURFACE_ELEVATED,
				"hover_border": StrontiumTokens.BORDER_STANDARD,
				"glow_color": StrontiumTokens.ACCENT_PRIMARY,
				"glow_alpha": 0.08,
				"glow_size": 4,
				"hover_glow_alpha": 0.16,
				"hover_glow_size": 8
			}

		PanelVariant.SECONDARY:
			return {
				"background": StrontiumTokens.SURFACE_SECONDARY,
				"border": StrontiumTokens.BORDER_SUBTLE,
				"hover_background": StrontiumTokens.SURFACE_ELEVATED,
				"hover_border": StrontiumTokens.BORDER_STANDARD,
				"glow_color": StrontiumTokens.ACCENT_PRIMARY,
				"glow_alpha": 0.08,
				"glow_size": 4,
				"hover_glow_alpha": 0.16,
				"hover_glow_size": 8
			}

		PanelVariant.ELEVATED:
			return {
				"background": StrontiumTokens.SURFACE_ELEVATED,
				"border": StrontiumTokens.BORDER_STANDARD,
				"hover_background": StrontiumTokens.SURFACE_ELEVATED,
				"hover_border": StrontiumTokens.ACCENT_PRIMARY,
				"glow_color": StrontiumTokens.ACCENT_PRIMARY,
				"glow_alpha": 0.12,
				"glow_size": 6,
				"hover_glow_alpha": 0.22,
				"hover_glow_size": 12
			}

		PanelVariant.OUTLINE:
			return {
				"background": Color.TRANSPARENT,
				"border": StrontiumTokens.BORDER_STANDARD,
				"hover_background": StrontiumTokens.SURFACE_PRIMARY,
				"hover_border": StrontiumTokens.ACCENT_PRIMARY,
				"glow_color": StrontiumTokens.ACCENT_PRIMARY,
				"glow_alpha": 0.08,
				"glow_size": 4,
				"hover_glow_alpha": 0.18,
				"hover_glow_size": 9
			}

		PanelVariant.ACTIVE:
			return {
				"background": StrontiumTokens.INTERACTION_ACTIVE,
				"border": StrontiumTokens.ACCENT_PRIMARY,
				"hover_background": StrontiumTokens.INTERACTION_ACTIVE,
				"hover_border": StrontiumTokens.ACCENT_PRIMARY,
				"glow_color": StrontiumTokens.ACCENT_PRIMARY,
				"glow_alpha": 0.22,
				"glow_size": 10,
				"hover_glow_alpha": 0.35,
				"hover_glow_size": 16
			}

		PanelVariant.WARNING:
			return {
				"background": StrontiumTokens.SURFACE_PRIMARY,
				"border": StrontiumTokens.STATE_WARNING,
				"hover_background": StrontiumTokens.SURFACE_ELEVATED,
				"hover_border": StrontiumTokens.STATE_WARNING,
				"glow_color": StrontiumTokens.STATE_WARNING,
				"glow_alpha": 0.12,
				"glow_size": 5,
				"hover_glow_alpha": 0.24,
				"hover_glow_size": 10
			}

		PanelVariant.ERROR:
			return {
				"background": StrontiumTokens.SURFACE_PRIMARY,
				"border": StrontiumTokens.STATE_ERROR,
				"hover_background": StrontiumTokens.SURFACE_ELEVATED,
				"hover_border": StrontiumTokens.STATE_ERROR,
				"glow_color": StrontiumTokens.STATE_ERROR,
				"glow_alpha": 0.12,
				"glow_size": 5,
				"hover_glow_alpha": 0.24,
				"hover_glow_size": 10
			}

	return {
		"background": StrontiumTokens.SURFACE_PRIMARY,
		"border": StrontiumTokens.BORDER_SUBTLE,
		"hover_background": StrontiumTokens.SURFACE_ELEVATED,
		"hover_border": StrontiumTokens.BORDER_STANDARD,
		"glow_color": StrontiumTokens.ACCENT_PRIMARY,
		"glow_alpha": 0.0,
		"glow_size": 0,
		"hover_glow_alpha": 0.0,
		"hover_glow_size": 0
	}


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
		StrontiumTokens.RADIUS_LARGE
	)

	style.corner_radius_top_right = (
		StrontiumTokens.RADIUS_LARGE
	)

	style.corner_radius_bottom_left = (
		StrontiumTokens.RADIUS_LARGE
	)

	style.corner_radius_bottom_right = (
		StrontiumTokens.RADIUS_LARGE
	)

	return style


func _configure_glow(
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


func _connect_signals() -> void:
	if not interactive:
		return

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


func _apply_state(
	animated: bool = true
) -> void:
	if current_style == null:
		return

	if hovered and interactive:
		_apply_hover_style(animated)
	else:
		_apply_normal_style(animated)


func _apply_normal_style(
	animated: bool
) -> void:
	_apply_style(
		current_style,
		animated
	)


func _apply_hover_style(
	animated: bool
) -> void:
	_apply_style(
		hover_style,
		animated
	)


func _apply_style(
	target_style: StyleBoxFlat,
	animated: bool
) -> void:
	if not animated:
		add_theme_stylebox_override(
			"panel",
			target_style
		)
		return

	var current_box := get_theme_stylebox(
        "panel"
	) as StyleBoxFlat

	if current_box == null:
		add_theme_stylebox_override(
			"panel",
			target_style
		)
		return

	_stop_transition()

	transition_tween = create_tween()

	transition_tween.set_parallel(true)

	transition_tween.set_trans(
		Tween.TRANS_QUAD
	)

	transition_tween.set_ease(
		Tween.EASE_OUT
	)

	transition_tween.tween_property(
		current_box,
		"bg_color",
		target_style.bg_color,
		StrontiumTokens.MOTION_STANDARD
	)

	transition_tween.tween_property(
		current_box,
		"border_color",
		target_style.border_color,
		StrontiumTokens.MOTION_STANDARD
	)

	transition_tween.tween_property(
		current_box,
		"shadow_color",
		target_style.shadow_color,
		StrontiumTokens.MOTION_STANDARD
	)

	transition_tween.tween_property(
		current_box,
		"shadow_size",
		target_style.shadow_size,
		StrontiumTokens.MOTION_STANDARD
	)


func _stop_transition() -> void:
	if (
		transition_tween != null
		and transition_tween.is_valid()
	):
		transition_tween.kill()

	transition_tween = null


func _on_mouse_entered() -> void:
	if not interactive:
		return

	hovered = true
	_apply_state()


func _on_mouse_exited() -> void:
	hovered = false

	if not interactive:
		return

	_apply_state()


func set_variant(
	new_variant: PanelVariant
) -> void:
	variant = new_variant
	hovered = false

	_build_styles()

	add_theme_stylebox_override(
		"panel",
		current_style
	)


func get_variant() -> PanelVariant:
	return variant


func set_padding(
	value: int
) -> void:
	padding = maxi(
		value,
		0
	)

	add_theme_constant_override(
		"margin_left",
		padding
	)

	add_theme_constant_override(
		"margin_top",
		padding
	)

	add_theme_constant_override(
		"margin_right",
		padding
	)

	add_theme_constant_override(
		"margin_bottom",
		padding
	)


func get_padding() -> int:
	return padding


func set_glow_enabled(
	enabled: bool
) -> void:
	glow_enabled = enabled

	_build_styles()
	_apply_state(false)


func is_glow_enabled() -> bool:
	return glow_enabled


func set_interactive(
	enabled: bool
) -> void:
	interactive = enabled
	hovered = false

	if interactive:
		mouse_filter = (
			Control.MOUSE_FILTER_STOP
		)

		_connect_signals()
	else:
		mouse_filter = (
			Control.MOUSE_FILTER_IGNORE
		)

	_apply_state(false)


func is_interactive() -> bool:
	return interactive


func refresh_style() -> void:
	_build_styles()
	_apply_state(false)


func _exit_tree() -> void:
	_stop_transition()
