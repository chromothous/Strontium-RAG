class_name StrontiumNotification
extends PanelContainer


enum NotificationVariant {
	INFO,
	SUCCESS,
	WARNING,
	ERROR,
	ACTIVE
}


signal notification_dismissed
signal notification_action_requested


@export var variant: NotificationVariant = NotificationVariant.INFO
@export var notification_title: String = ""
@export var notification_message: String = ""
@export var dismissible: bool = true
@export var auto_dismiss: bool = false
@export var auto_dismiss_seconds: float = 5.0
@export var glow_enabled: bool = true


var accent_strip: ColorRect
var state_indicator: ColorRect
var title_label: Label
var message_label: Label
var close_button: Button
var content_container: VBoxContainer
var body_container: HBoxContainer
var dismiss_timer: Timer

var notification_style: StyleBoxFlat


func _ready() -> void:
	_build_notification()
	_build_style()
	_apply_style()

	if auto_dismiss:
		_start_auto_dismiss()


func _build_notification() -> void:
	custom_minimum_size = Vector2(
		360.0,
		86.0
	)

	mouse_filter = Control.MOUSE_FILTER_STOP

	body_container = HBoxContainer.new()
	body_container.name = "BodyContainer"

	add_child(body_container)

	body_container.set_anchors_and_offsets_preset(
		Control.PRESET_FULL_RECT
	)

	body_container.add_theme_constant_override(
		"separation",
		12
	)

	accent_strip = ColorRect.new()
	accent_strip.name = "AccentStrip"
	accent_strip.custom_minimum_size = Vector2(
		4.0,
		0.0
	)

	body_container.add_child(
		accent_strip
	)

	state_indicator = ColorRect.new()
	state_indicator.name = "StateIndicator"
	state_indicator.custom_minimum_size = Vector2(
		10.0,
		10.0
	)

	body_container.add_child(
		state_indicator
	)

	content_container = VBoxContainer.new()
	content_container.name = "Content"

	content_container.size_flags_horizontal = (
		Control.SIZE_EXPAND_FILL
	)

	content_container.add_theme_constant_override(
		"separation",
		4
	)

	body_container.add_child(
		content_container
	)

	title_label = Label.new()
	title_label.name = "Title"

	title_label.text = notification_title
	title_label.text_overrun_behavior = (
		TextServer.OVERRUN_TRIM_ELLIPSIS
	)

	title_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_PRIMARY
	)

	title_label.add_theme_font_size_override(
		"font_size",
		16
	)

	content_container.add_child(
		title_label
	)

	message_label = Label.new()
	message_label.name = "Message"

	message_label.text = notification_message
	message_label.autowrap_mode = (
		TextServer.AUTOWRAP_WORD_SMART
	)

	message_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	message_label.add_theme_font_size_override(
		"font_size",
		14
	)

	content_container.add_child(
		message_label
	)

	close_button = Button.new()
	close_button.name = "CloseButton"
	close_button.text = "×"
	close_button.focus_mode = Control.FOCUS_ALL
	close_button.mouse_default_cursor_shape = (
		Control.CURSOR_POINTING_HAND
	)

	close_button.custom_minimum_size = Vector2(
		32.0,
		32.0
	)

	close_button.visible = dismissible

	close_button.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	close_button.add_theme_color_override(
		"font_hover_color",
		StrontiumTokens.TEXT_PRIMARY
	)

	body_container.add_child(
		close_button
	)

	if not close_button.pressed.is_connected(
		_on_close_pressed
	):
		close_button.pressed.connect(
			_on_close_pressed
	)

	dismiss_timer = Timer.new()
	dismiss_timer.name = "DismissTimer"
	dismiss_timer.one_shot = true

	add_child(
		dismiss_timer
	)

	if not dismiss_timer.timeout.is_connected(
		_on_dismiss_timer_timeout
	):
		dismiss_timer.timeout.connect(
			_on_dismiss_timer_timeout
	)


func _build_style() -> void:
	var accent_color := _get_variant_color()

	notification_style = StyleBoxFlat.new()

	notification_style.bg_color = (
		StrontiumTokens.BORDER_STANDARD.darkened(
			0.45
		)
	)

	notification_style.border_width_left = 1
	notification_style.border_width_top = 1
	notification_style.border_width_right = 1
	notification_style.border_width_bottom = 1

	notification_style.border_color = Color(
		accent_color,
		0.55
	)

	notification_style.corner_radius_top_left = 8
	notification_style.corner_radius_top_right = 8
	notification_style.corner_radius_bottom_left = 8
	notification_style.corner_radius_bottom_right = 8

	notification_style.content_margin_left = 12
	notification_style.content_margin_top = 12
	notification_style.content_margin_right = 12
	notification_style.content_margin_bottom = 12

	if glow_enabled:
		notification_style.shadow_color = Color(
			accent_color,
			0.22
		)

		notification_style.shadow_size = 8
	else:
		notification_style.shadow_color = Color.TRANSPARENT
		notification_style.shadow_size = 0


func _apply_style() -> void:
	add_theme_stylebox_override(
		"panel",
		notification_style
	)

	var accent_color := _get_variant_color()

	accent_strip.color = accent_color
	state_indicator.color = accent_color


func _get_variant_color() -> Color:
	match variant:
		NotificationVariant.INFO:
			return StrontiumTokens.ACCENT_PRIMARY

		NotificationVariant.SUCCESS:
			return StrontiumTokens.STATE_SUCCESS

		NotificationVariant.WARNING:
			return StrontiumTokens.STATE_WARNING

		NotificationVariant.ERROR:
			return StrontiumTokens.STATE_ERROR

		NotificationVariant.ACTIVE:
			return StrontiumTokens.SPECTRUM_VIOLET

	return StrontiumTokens.ACCENT_PRIMARY


func set_variant(
	new_variant: NotificationVariant
) -> void:
	variant = new_variant

	_build_style()
	_apply_style()


func get_variant() -> NotificationVariant:
	return variant


func set_notification_title(
	new_title: String
) -> void:
	notification_title = new_title

	if title_label != null:
		title_label.text = new_title


func get_notification_title() -> String:
	return notification_title


func set_notification_message(
	new_message: String
) -> void:
	notification_message = new_message

	if message_label != null:
		message_label.text = new_message


func get_notification_message() -> String:
	return notification_message


func set_dismissible(
	enabled: bool
) -> void:
	dismissible = enabled

	if close_button != null:
		close_button.visible = enabled


func is_dismissible() -> bool:
	return dismissible


func set_auto_dismiss(
	enabled: bool,
	seconds: float = 5.0
) -> void:
	auto_dismiss = enabled
	auto_dismiss_seconds = maxf(
		seconds,
		0.1
	)

	if not auto_dismiss and dismiss_timer != null:
		dismiss_timer.stop()


func is_auto_dismiss_enabled() -> bool:
	return auto_dismiss


func set_auto_dismiss_seconds(
	seconds: float
) -> void:
	auto_dismiss_seconds = maxf(
		seconds,
		0.1
	)


func get_auto_dismiss_seconds() -> float:
	return auto_dismiss_seconds


func set_glow_enabled(
	enabled: bool
) -> void:
	glow_enabled = enabled

	_build_style()
	_apply_style()


func is_glow_enabled() -> bool:
	return glow_enabled


func show_notification(
	new_title: String,
	new_message: String,
	new_variant: NotificationVariant = NotificationVariant.INFO
) -> void:
	set_variant(
		new_variant
	)

	set_notification_title(
		new_title
	)

	set_notification_message(
		new_message
	)

	show()

	if auto_dismiss:
		_start_auto_dismiss()


func dismiss_notification() -> void:
	if dismiss_timer != null:
		dismiss_timer.stop()

	hide()

	notification_dismissed.emit()


func _start_auto_dismiss() -> void:
	if dismiss_timer == null:
		return

	dismiss_timer.wait_time = maxf(
		auto_dismiss_seconds,
		0.1
	)

	dismiss_timer.start()


func _on_close_pressed() -> void:
	dismiss_notification()


func _on_dismiss_timer_timeout() -> void:
	dismiss_notification()
