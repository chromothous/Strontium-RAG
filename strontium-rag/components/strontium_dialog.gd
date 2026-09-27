class_name StrontiumDialog
extends PanelContainer


enum DialogVariant {
	INFO,
	CONFIRMATION,
	WARNING,
	ERROR
}


signal confirmed
signal cancelled
signal dialog_closed


@export var variant: DialogVariant = DialogVariant.INFO
@export var dialog_title: String = ""
@export var dialog_message: String = ""
@export var confirm_text: String = "Confirm"
@export var cancel_text: String = "Cancel"
@export var show_cancel: bool = true
@export var glow_enabled: bool = true


var content_container: VBoxContainer
var header_container: HBoxContainer
var button_container: HBoxContainer

var title_label: Label
var message_label: Label

var confirm_button: StrontiumButton
var cancel_button: StrontiumButton

var dialog_style: StyleBoxFlat
var accent_strip: ColorRect


func _ready() -> void:
	_build_dialog()
	_build_style()
	_apply_style()


func _build_dialog() -> void:
	custom_minimum_size = Vector2(
		460.0,
		220.0
	)

	mouse_filter = Control.MOUSE_FILTER_STOP

	content_container = VBoxContainer.new()
	content_container.name = "Content"

	content_container.add_theme_constant_override(
		"separation",
		16
	)

	add_child(content_container)

	accent_strip = ColorRect.new()
	accent_strip.name = "AccentStrip"
	accent_strip.custom_minimum_size = Vector2(
		0.0,
		4.0
	)

	content_container.add_child(
		accent_strip
	)

	header_container = HBoxContainer.new()
	header_container.name = "Header"

	header_container.add_theme_constant_override(
		"separation",
		10
	)

	content_container.add_child(
		header_container
	)

	title_label = Label.new()
	title_label.name = "Title"
	title_label.text = dialog_title

	title_label.size_flags_horizontal = (
		Control.SIZE_EXPAND_FILL
	)

	title_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_PRIMARY
	)

	title_label.add_theme_font_size_override(
		"font_size",
		20
	)

	header_container.add_child(
		title_label
	)

	message_label = Label.new()
	message_label.name = "Message"
	message_label.text = dialog_message

	message_label.autowrap_mode = (
		TextServer.AUTOWRAP_WORD_SMART
	)

	message_label.size_flags_vertical = (
		Control.SIZE_EXPAND_FILL
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

	button_container = HBoxContainer.new()
	button_container.name = "Buttons"

	button_container.alignment = BoxContainer.ALIGNMENT_END

	button_container.add_theme_constant_override(
		"separation",
		10
	)

	content_container.add_child(
		button_container
	)

	cancel_button = StrontiumButton.new()
	cancel_button.name = "CancelButton"
	cancel_button.text = cancel_text
	cancel_button.variant = (
		StrontiumButton.ButtonVariant.GHOST
	)

	cancel_button.custom_minimum_size = Vector2(
		100.0,
		38.0
	)

	cancel_button.pressed.connect(
		_on_cancel_pressed
	)

	button_container.add_child(
		cancel_button
	)

	confirm_button = StrontiumButton.new()
	confirm_button.name = "ConfirmButton"
	confirm_button.text = confirm_text
	confirm_button.variant = (
		StrontiumButton.ButtonVariant.PRIMARY
	)

	confirm_button.custom_minimum_size = Vector2(
		110.0,
		38.0
	)

	confirm_button.pressed.connect(
		_on_confirm_pressed
	)

	button_container.add_child(
		confirm_button
	)

	_update_variant_controls()


func _build_style() -> void:
	var accent_color := _get_variant_color()

	dialog_style = StyleBoxFlat.new()

	dialog_style.bg_color = (
		StrontiumTokens.BORDER_STANDARD.darkened(
			0.55
		)
	)

	dialog_style.border_width_left = 1
	dialog_style.border_width_top = 1
	dialog_style.border_width_right = 1
	dialog_style.border_width_bottom = 1

	dialog_style.border_color = Color(
		accent_color,
		0.60
	)

	dialog_style.corner_radius_top_left = 10
	dialog_style.corner_radius_top_right = 10
	dialog_style.corner_radius_bottom_left = 10
	dialog_style.corner_radius_bottom_right = 10

	dialog_style.content_margin_left = 20
	dialog_style.content_margin_top = 18
	dialog_style.content_margin_right = 20
	dialog_style.content_margin_bottom = 20

	if glow_enabled:
		dialog_style.shadow_color = Color(
			accent_color,
			0.25
		)

		dialog_style.shadow_size = 12
	else:
		dialog_style.shadow_color = Color.TRANSPARENT
		dialog_style.shadow_size = 0


func _apply_style() -> void:
	add_theme_stylebox_override(
		"panel",
		dialog_style
	)

	if accent_strip != null:
		accent_strip.color = _get_variant_color()


func _get_variant_color() -> Color:
	match variant:
		DialogVariant.INFO:
			return StrontiumTokens.ACCENT_PRIMARY

		DialogVariant.CONFIRMATION:
			return StrontiumTokens.STATE_SUCCESS

		DialogVariant.WARNING:
			return StrontiumTokens.STATE_WARNING

		DialogVariant.ERROR:
			return StrontiumTokens.STATE_ERROR

	return StrontiumTokens.ACCENT_PRIMARY


func _update_variant_controls() -> void:
	if confirm_button == null:
		return

	match variant:
		DialogVariant.ERROR:
			confirm_button.variant = (
				StrontiumButton.ButtonVariant.DANGER
			)

		DialogVariant.WARNING:
			confirm_button.variant = (
				StrontiumButton.ButtonVariant.PRIMARY
			)

		_:
			confirm_button.variant = (
				StrontiumButton.ButtonVariant.PRIMARY
			)

	cancel_button.visible = show_cancel


func set_variant(
	new_variant: DialogVariant
) -> void:
	variant = new_variant

	_update_variant_controls()
	_build_style()
	_apply_style()


func get_variant() -> DialogVariant:
	return variant


func set_dialog_title(
	new_title: String
) -> void:
	dialog_title = new_title

	if title_label != null:
		title_label.text = new_title


func get_dialog_title() -> String:
	return dialog_title


func set_dialog_message(
	new_message: String
) -> void:
	dialog_message = new_message

	if message_label != null:
		message_label.text = new_message


func get_dialog_message() -> String:
	return dialog_message


func set_confirm_text(
	new_text: String
) -> void:
	confirm_text = new_text

	if confirm_button != null:
		confirm_button.text = new_text


func get_confirm_text() -> String:
	return confirm_text


func set_cancel_text(
	new_text: String
) -> void:
	cancel_text = new_text

	if cancel_button != null:
		cancel_button.text = new_text


func get_cancel_text() -> String:
	return cancel_text


func set_cancel_visible(
	visible: bool
) -> void:
	show_cancel = visible

	if cancel_button != null:
		cancel_button.visible = visible


func is_cancel_visible() -> bool:
	return show_cancel


func set_glow_enabled(
	enabled: bool
) -> void:
	glow_enabled = enabled

	_build_style()
	_apply_style()


func is_glow_enabled() -> bool:
	return glow_enabled


func open_dialog(
	new_title: String,
	new_message: String,
	new_variant: DialogVariant = DialogVariant.INFO,
	new_confirm_text: String = "Confirm",
	new_cancel_text: String = "Cancel"
) -> void:
	set_variant(
		new_variant
	)

	set_dialog_title(
		new_title
	)

	set_dialog_message(
		new_message
	)

	set_confirm_text(
		new_confirm_text
	)

	set_cancel_text(
		new_cancel_text
	)

	show()


func close_dialog() -> void:
	hide()
	dialog_closed.emit()


func _on_confirm_pressed() -> void:
	confirmed.emit()
	dialog_closed.emit()
	hide()


func _on_cancel_pressed() -> void:
	cancelled.emit()
	dialog_closed.emit()
	hide()
