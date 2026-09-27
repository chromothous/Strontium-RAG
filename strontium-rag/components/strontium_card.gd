class_name StrontiumCard
extends PanelContainer


enum InteractionState {
	NORMAL,
	HOVER,
	ACTIVE
}


@export var card_size: Vector2 = Vector2(360, 180)
@export var padding: int = StrontiumTokens.SPACE_LG
@export var glow_enabled: bool = true
@export var elevated: bool = false
@export var interactive: bool = true


var interaction_state: InteractionState = InteractionState.NORMAL
var current_style: StyleBoxFlat
var transition_tween: Tween


func _ready() -> void:
	custom_minimum_size = card_size
	mouse_filter = Control.MOUSE_FILTER_STOP
	set_process_input(true)

	_apply_content_mouse_behavior()
	_connect_mouse_signals()
	_apply_card_style()


func _apply_content_mouse_behavior() -> void:
	for child in get_children():
		if child is Control:
			child.mouse_filter = Control.MOUSE_FILTER_IGNORE


func _connect_mouse_signals() -> void:
	if not interactive:
		return

	if not mouse_entered.is_connected(_on_mouse_entered):
		mouse_entered.connect(_on_mouse_entered)

	if not mouse_exited.is_connected(_on_mouse_exited):
		mouse_exited.connect(_on_mouse_exited)

	if not gui_input.is_connected(_on_gui_input):
		gui_input.connect(_on_gui_input)


func _apply_card_style() -> void:
	current_style = StyleBoxFlat.new()

	current_style.corner_radius_top_left = StrontiumTokens.RADIUS_STANDARD
	current_style.corner_radius_top_right = StrontiumTokens.RADIUS_STANDARD
	current_style.corner_radius_bottom_left = StrontiumTokens.RADIUS_STANDARD
	current_style.corner_radius_bottom_right = StrontiumTokens.RADIUS_STANDARD

	_apply_state_instant(InteractionState.NORMAL)


func _apply_state_instant(new_state: InteractionState) -> void:
	interaction_state = new_state

	match interaction_state:
		InteractionState.NORMAL:
			_apply_normal_state()
		InteractionState.HOVER:
			_apply_hover_state()
		InteractionState.ACTIVE:
			_apply_active_state()

	add_theme_stylebox_override("panel", current_style)

	add_theme_constant_override("margin_left", padding)
	add_theme_constant_override("margin_top", padding)
	add_theme_constant_override("margin_right", padding)
	add_theme_constant_override("margin_bottom", padding)


func _apply_normal_state() -> void:
	if elevated:
		current_style.bg_color = StrontiumTokens.SURFACE_ELEVATED
		current_style.border_color = StrontiumTokens.BORDER_STANDARD
	else:
		current_style.bg_color = StrontiumTokens.SURFACE_PRIMARY
		current_style.border_color = StrontiumTokens.BORDER_SUBTLE

	current_style.set_border_width(SIDE_LEFT, 1)
	current_style.set_border_width(SIDE_TOP, 1)
	current_style.set_border_width(SIDE_RIGHT, 1)
	current_style.set_border_width(SIDE_BOTTOM, 1)

	current_style.shadow_color = Color.TRANSPARENT
	current_style.shadow_size = 0


func _apply_hover_state() -> void:
	current_style.bg_color = Color("#24364D")
	current_style.border_color = StrontiumTokens.ACCENT_PRIMARY

	current_style.set_border_width(SIDE_LEFT, 3)
	current_style.set_border_width(SIDE_TOP, 3)
	current_style.set_border_width(SIDE_RIGHT, 3)
	current_style.set_border_width(SIDE_BOTTOM, 3)

	if glow_enabled:
		current_style.shadow_color = Color(
			StrontiumTokens.ACCENT_PRIMARY,
			0.65
		)
		current_style.shadow_size = 20
	else:
		current_style.shadow_color = Color.TRANSPARENT
		current_style.shadow_size = 0


func _apply_active_state() -> void:
	current_style.bg_color = StrontiumTokens.INTERACTION_ACTIVE
	current_style.border_color = StrontiumTokens.SPECTRUM_VIOLET

	current_style.set_border_width(SIDE_LEFT, 4)
	current_style.set_border_width(SIDE_TOP, 4)
	current_style.set_border_width(SIDE_RIGHT, 4)
	current_style.set_border_width(SIDE_BOTTOM, 4)

	if glow_enabled:
		current_style.shadow_color = Color(
			StrontiumTokens.SPECTRUM_VIOLET,
			0.85
		)
		current_style.shadow_size = 28
	else:
		current_style.shadow_color = Color.TRANSPARENT
		current_style.shadow_size = 0


func _transition_to(
	new_state: InteractionState,
	duration: float
) -> void:
	if current_style == null:
		return

	interaction_state = new_state

	var target_background := StrontiumTokens.SURFACE_PRIMARY
	var target_border := StrontiumTokens.BORDER_SUBTLE
	var target_border_width := 1
	var target_glow_color := Color.TRANSPARENT
	var target_glow_size := 0

	match new_state:
		InteractionState.NORMAL:
			if elevated:
				target_background = StrontiumTokens.SURFACE_ELEVATED
				target_border = StrontiumTokens.BORDER_STANDARD

			target_border_width = 1
			target_glow_color = Color.TRANSPARENT
			target_glow_size = 0

		InteractionState.HOVER:
			target_background = Color("#24364D")
			target_border = StrontiumTokens.ACCENT_PRIMARY
			target_border_width = 3

			if glow_enabled:
				target_glow_color = Color(
					StrontiumTokens.ACCENT_PRIMARY,
					0.65
				)
				target_glow_size = 20

		InteractionState.ACTIVE:
			target_background = StrontiumTokens.INTERACTION_ACTIVE
			target_border = StrontiumTokens.SPECTRUM_VIOLET
			target_border_width = 4

			if glow_enabled:
				target_glow_color = Color(
					StrontiumTokens.SPECTRUM_VIOLET,
					0.85
				)
				target_glow_size = 28

	if transition_tween != null and transition_tween.is_valid():
		transition_tween.kill()

	transition_tween = create_tween()
	transition_tween.set_parallel(true)
	transition_tween.set_trans(Tween.TRANS_QUAD)
	transition_tween.set_ease(Tween.EASE_OUT)

	transition_tween.tween_property(
		current_style,
		"bg_color",
		target_background,
		duration
	)

	transition_tween.tween_property(
		current_style,
		"border_color",
		target_border,
		duration
	)

	transition_tween.tween_method(
		_set_border_width,
		current_style.get_border_width(SIDE_LEFT),
		target_border_width,
		duration
	)

	transition_tween.tween_property(
		current_style,
		"shadow_color",
		target_glow_color,
		duration
	)

	transition_tween.tween_property(
		current_style,
		"shadow_size",
		target_glow_size,
		duration
	)


func _set_border_width(value: float) -> void:
	var width := int(round(value))

	current_style.set_border_width(SIDE_LEFT, width)
	current_style.set_border_width(SIDE_TOP, width)
	current_style.set_border_width(SIDE_RIGHT, width)
	current_style.set_border_width(SIDE_BOTTOM, width)


func _on_mouse_entered() -> void:
	if not interactive:
		return

	if interaction_state == InteractionState.ACTIVE:
		return

	print("[DEBUG] StrontiumCard → HOVER")

	_transition_to(
		InteractionState.HOVER,
		StrontiumTokens.MOTION_HOVER
	)


func _on_mouse_exited() -> void:
	if not interactive:
		return

	if interaction_state == InteractionState.ACTIVE:
		return

	print("[DEBUG] StrontiumCard → NORMAL")

	_transition_to(
		InteractionState.NORMAL,
		StrontiumTokens.MOTION_EXIT
	)


func _on_gui_input(event: InputEvent) -> void:
	if not interactive:
		return

	if event is InputEventMouseButton:
		var mouse_event := event as InputEventMouseButton

		if mouse_event.button_index == MOUSE_BUTTON_LEFT:
			if mouse_event.pressed:
				print("[DEBUG] StrontiumCard → ACTIVE")

				_transition_to(
					InteractionState.ACTIVE,
					StrontiumTokens.MOTION_ACTIVE
				)


func _input(event: InputEvent) -> void:
	if not interactive:
		return

	if interaction_state != InteractionState.ACTIVE:
		return

	if event is InputEventMouseButton:
		var mouse_event := event as InputEventMouseButton

		if mouse_event.button_index != MOUSE_BUTTON_LEFT:
			return

		if mouse_event.pressed:
			return

		var mouse_position := get_global_mouse_position()
		var mouse_inside := get_global_rect().has_point(
			mouse_position
		)

		if mouse_inside:
			print("[DEBUG] StrontiumCard → HOVER")

			_transition_to(
				InteractionState.HOVER,
				StrontiumTokens.MOTION_HOVER
			)
		else:
			print("[DEBUG] StrontiumCard → NORMAL")

			_transition_to(
				InteractionState.NORMAL,
				StrontiumTokens.MOTION_EXIT
			)


func set_interactive(value: bool) -> void:
	interactive = value

	if not interactive:
		interaction_state = InteractionState.NORMAL
		_apply_content_mouse_behavior()
		_apply_disabled_state()
	else:
		mouse_filter = Control.MOUSE_FILTER_STOP
		_connect_mouse_signals()

		_transition_to(
			InteractionState.NORMAL,
			StrontiumTokens.MOTION_STANDARD
		)


func _apply_disabled_state() -> void:
	if current_style == null:
		return

	current_style.bg_color = StrontiumTokens.SURFACE_PRIMARY
	current_style.border_color = StrontiumTokens.INTERACTION_DISABLED

	current_style.set_border_width(SIDE_LEFT, 1)
	current_style.set_border_width(SIDE_TOP, 1)
	current_style.set_border_width(SIDE_RIGHT, 1)
	current_style.set_border_width(SIDE_BOTTOM, 1)

	current_style.shadow_color = Color.TRANSPARENT
	current_style.shadow_size = 0

	add_theme_color_override(
		"font_color",
		StrontiumTokens.INTERACTION_DISABLED
	)

	add_theme_stylebox_override(
		"panel",
		current_style
	)


func set_interaction_state(
	new_state: InteractionState
) -> void:
	if not interactive:
		return

	_transition_to(
		new_state,
		StrontiumTokens.MOTION_STANDARD
	)
