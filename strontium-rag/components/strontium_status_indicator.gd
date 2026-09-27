class_name StrontiumStatusIndicator
extends HBoxContainer


signal status_changed(
	status_text: String,
	status_type: StatusType
)


enum StatusType {
	INFO,
	SUCCESS,
	WARNING,
	ERROR,
	ACTIVE,
	IDLE
}


var status_label: Label
var status_indicator: Panel
var status_icon: StrontiumIcon
var activity_indicator: StrontiumActivityIndicator

var pulse_tween: Tween

var current_status: StatusType = StatusType.IDLE
var current_color: Color = StrontiumTokens.TEXT_MUTED


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE

	add_theme_constant_override(
		"separation",
		StrontiumTokens.SPACE_SM
	)

	_build()

	set_status(
		"IDLE",
		StatusType.IDLE
	)


func _build() -> void:
	status_indicator = Panel.new()
	status_indicator.name = "Indicator"
	status_indicator.custom_minimum_size = Vector2(
		10,
		10
	)
	status_indicator.mouse_filter = (
		Control.MOUSE_FILTER_IGNORE
	)

	add_child(status_indicator)

	status_icon = StrontiumIcon.new()
	status_icon.name = "StatusIcon"
	status_icon.icon_size = 14.0
	status_icon.stroke_width = 1.6
	status_icon.mouse_filter = (
		Control.MOUSE_FILTER_IGNORE
	)
	status_icon.visible = false

	add_child(status_icon)

	activity_indicator = (
		StrontiumActivityIndicator.new()
	)

	activity_indicator.name = (
        "ActivityIndicator"
	)

	activity_indicator.set_indicator_color(
		StrontiumTokens.ACCENT_PRIMARY
	)

	activity_indicator.stop()
	activity_indicator.visible = false

	add_child(activity_indicator)

	status_label = Label.new()
	status_label.name = "Label"
	status_label.mouse_filter = (
		Control.MOUSE_FILTER_IGNORE
	)

	status_label.add_theme_font_size_override(
		"font_size",
		StrontiumTokens.FONT_SIZE_CAPTION
	)

	status_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_MUTED
	)

	add_child(status_label)


func set_status(
	text: String,
	type: StatusType
) -> void:
	if status_label == null:
		return

	var had_previous_status: bool = (
		not status_label.text.is_empty()
	)

	current_status = type
	current_color = _get_status_color(type)

	status_label.text = text.to_upper()

	_apply_visual_state()
	_update_activity()
	_update_icon()

	if had_previous_status:
		_play_transition_pulse()

	status_changed.emit(
		status_label.text,
		current_status
	)


func set_info(
	text: String
) -> void:
	set_status(
		text,
		StatusType.INFO
	)


func set_success(
	text: String
) -> void:
	set_status(
		text,
		StatusType.SUCCESS
	)


func set_warning(
	text: String
) -> void:
	set_status(
		text,
		StatusType.WARNING
	)


func set_error(
	text: String
) -> void:
	set_status(
		text,
		StatusType.ERROR
	)


func set_active(
	text: String
) -> void:
	set_status(
		text,
		StatusType.ACTIVE
	)


func set_idle(
	text: String
) -> void:
	set_status(
		text,
		StatusType.IDLE
	)


func set_status_color(
	text: String,
	color: Color
) -> void:
	if status_label == null:
		return

	var had_previous_status: bool = (
		not status_label.text.is_empty()
	)

	current_status = StatusType.INFO
	current_color = color

	status_label.text = text.to_upper()

	_apply_visual_state()
	_update_activity()
	_update_icon()

	if had_previous_status:
		_play_transition_pulse()

	status_changed.emit(
		status_label.text,
		current_status
	)


func _get_status_color(
	type: StatusType
) -> Color:
	match type:
		StatusType.INFO:
			return StrontiumTokens.STATE_INFO

		StatusType.SUCCESS:
			return StrontiumTokens.STATE_SUCCESS

		StatusType.WARNING:
			return StrontiumTokens.STATE_WARNING

		StatusType.ERROR:
			return StrontiumTokens.STATE_ERROR

		StatusType.ACTIVE:
			return StrontiumTokens.ACCENT_PRIMARY

		StatusType.IDLE:
			return StrontiumTokens.TEXT_MUTED

	return StrontiumTokens.TEXT_MUTED


func _get_status_icon(
	type: StatusType
) -> StrontiumIcon.IconType:
	match type:
		StatusType.INFO:
			return StrontiumIcon.IconType.INFO

		StatusType.SUCCESS:
			return StrontiumIcon.IconType.CHECK

		StatusType.WARNING:
			return StrontiumIcon.IconType.WARNING

		StatusType.ERROR:
			return StrontiumIcon.IconType.ERROR

		StatusType.ACTIVE:
			return StrontiumIcon.IconType.ACTIVITY

		StatusType.IDLE:
			return StrontiumIcon.IconType.INFO

	return StrontiumIcon.IconType.INFO


func _get_icon_glow_strength(
	type: StatusType
) -> float:
	match type:
		StatusType.INFO:
			return 0.18

		StatusType.SUCCESS:
			return 0.22

		StatusType.WARNING:
			return 0.35

		StatusType.ERROR:
			return 0.45

		StatusType.ACTIVE:
			return 0.40

		StatusType.IDLE:
			return 0.0

	return 0.0


func _should_icon_glow(
	type: StatusType
) -> bool:
	return (
		type != StatusType.IDLE
		and type != StatusType.ACTIVE
	)


func _apply_visual_state() -> void:
	if not is_instance_valid(
		status_indicator
	):
		return

	var style := StyleBoxFlat.new()

	style.bg_color = current_color

	style.corner_radius_top_left = 5
	style.corner_radius_top_right = 5
	style.corner_radius_bottom_left = 5
	style.corner_radius_bottom_right = 5

	match current_status:
		StatusType.INFO:
			style.shadow_color = Color(
				current_color,
				0.25
			)
			style.shadow_size = 4

		StatusType.SUCCESS:
			style.shadow_color = Color(
				current_color,
				0.25
			)
			style.shadow_size = 4

		StatusType.WARNING:
			style.shadow_color = Color(
				current_color,
				0.30
			)
			style.shadow_size = 5

		StatusType.ERROR:
			style.shadow_color = Color(
				current_color,
				0.35
			)
			style.shadow_size = 6

		StatusType.ACTIVE:
			style.shadow_color = Color(
				current_color,
				0.55
			)
			style.shadow_size = 8

		StatusType.IDLE:
			style.shadow_color = Color.TRANSPARENT
			style.shadow_size = 0

	status_indicator.add_theme_stylebox_override(
		"panel",
		style
	)

	status_label.add_theme_color_override(
		"font_color",
		current_color
	)


func _update_icon() -> void:
	if not is_instance_valid(
		status_icon
	):
		return

	if current_status == StatusType.ACTIVE:
		status_icon.visible = false
		status_icon.set_glow(
			false
		)
		return

	status_icon.visible = true

	status_icon.set_icon(
		_get_status_icon(
			current_status
		)
	)

	status_icon.set_icon_color(
		current_color
	)

	status_icon.set_icon_size(
		14.0
	)

	status_icon.set_stroke_width(
		1.6
	)

	if _should_icon_glow(
		current_status
	):
		status_icon.set_glow(
			true,
			_get_icon_glow_strength(
				current_status
			)
		)
	else:
		status_icon.set_glow(
			false
		)


func _update_activity() -> void:
	if not is_instance_valid(
		activity_indicator
	):
		return

	var active: bool = (
		current_status == StatusType.ACTIVE
	)

	status_indicator.visible = (
		not active
		and current_status == StatusType.IDLE
	)

	activity_indicator.visible = active

	if active:
		activity_indicator.set_indicator_color(
			StrontiumTokens.ACCENT_PRIMARY
		)

		activity_indicator.play()
	else:
		activity_indicator.stop()


func _play_transition_pulse() -> void:
	if status_label == null:
		return

	_stop_pulse()

	var target: Control = null

	if current_status == StatusType.ACTIVE:
		if is_instance_valid(
			activity_indicator
		):
			target = activity_indicator

	elif (
		is_instance_valid(status_icon)
		and status_icon.visible
	):
		target = status_icon

	elif is_instance_valid(
		status_indicator
	):
		target = status_indicator

	if target == null:
		return

	target.scale = Vector2(
		0.82,
		0.82
	)

	target.modulate.a = 0.65

	pulse_tween = create_tween()

	pulse_tween.set_trans(
		Tween.TRANS_QUAD
	)

	pulse_tween.set_ease(
		Tween.EASE_OUT
	)

	pulse_tween.set_parallel(true)

	pulse_tween.tween_property(
		target,
		"scale",
		Vector2.ONE,
		StrontiumTokens.MOTION_STANDARD
	)

	pulse_tween.tween_property(
		target,
		"modulate:a",
		1.0,
		StrontiumTokens.MOTION_STANDARD
	)


func _stop_pulse() -> void:
	if (
		pulse_tween != null
		and pulse_tween.is_valid()
	):
		pulse_tween.kill()

	pulse_tween = null

	if is_instance_valid(
		status_indicator
	):
		status_indicator.scale = Vector2.ONE
		status_indicator.modulate.a = 1.0

	if is_instance_valid(
		status_icon
	):
		status_icon.scale = Vector2.ONE
		status_icon.modulate.a = 1.0

	if is_instance_valid(
		activity_indicator
	):
		activity_indicator.scale = Vector2.ONE
		activity_indicator.modulate.a = 1.0


func set_custom_status(
	text: String,
	color: Color
) -> void:
	set_status_color(
		text,
		color
	)
