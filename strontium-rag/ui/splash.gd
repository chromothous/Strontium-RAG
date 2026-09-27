class_name StrontiumSplash
extends Control


signal splash_completed
signal transition_requested


@export var minimum_display_time: float = 0.75
@export var fade_duration: float = 0.35
@export var glow_enabled: bool = true


var background: ColorRect
var content: VBoxContainer
var logo_label: Label
var product_label: Label
var spectrum: StrontiumSpectrum
var activity: StrontiumActivityIndicator
var status_label: Label
var detail_label: Label
var progress_label: Label

var display_timer: Timer
var minimum_time_elapsed: bool = false
var completion_requested: bool = false
var transition_started: bool = false


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_STOP

	set_anchors_and_offsets_preset(
		Control.PRESET_FULL_RECT
	)

	_build_interface()
	_start_display_timer()


func _build_interface() -> void:
	background = ColorRect.new()
	background.name = "Background"

	background.color = Color(
		0.018,
		0.022,
		0.035,
		1.0
	)

	background.mouse_filter = (
		Control.MOUSE_FILTER_IGNORE
	)

	add_child(
		background
	)

	background.set_anchors_and_offsets_preset(
		Control.PRESET_FULL_RECT
	)

	content = VBoxContainer.new()
	content.name = "Content"

	content.set_anchors_preset(
		Control.PRESET_CENTER
	)

	content.position = Vector2(
		-220.0,
		-150.0
	)

	content.size = Vector2(
		440.0,
		300.0
	)

	content.alignment = (
		BoxContainer.ALIGNMENT_CENTER
	)

	content.add_theme_constant_override(
		"separation",
		10
	)

	add_child(
		content
	)

	logo_label = Label.new()
	logo_label.name = "Logo"

	logo_label.text = "STRONTIUM"

	logo_label.horizontal_alignment = (
		HORIZONTAL_ALIGNMENT_CENTER
	)

	logo_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_PRIMARY
	)

	logo_label.add_theme_font_size_override(
		"font_size",
		42
	)

	content.add_child(
		logo_label
	)

	product_label = Label.new()
	product_label.name = "Product"

	product_label.text = (
		"LABS // STRONTIUM RAG"
	)

	product_label.horizontal_alignment = (
		HORIZONTAL_ALIGNMENT_CENTER
	)

	product_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.ACCENT_PRIMARY
	)

	product_label.add_theme_font_size_override(
		"font_size",
		14
	)

	content.add_child(
		product_label
	)

	spectrum = StrontiumSpectrum.new()
	spectrum.name = "Spectrum"

	spectrum.custom_minimum_size = Vector2(
		420.0,
		8.0
	)

	spectrum.mouse_filter = (
		Control.MOUSE_FILTER_IGNORE
	)

	content.add_child(
		spectrum
	)

	activity = StrontiumActivityIndicator.new()
	activity.name = "Activity"

	activity.custom_minimum_size = Vector2(
		60.0,
		18.0
	)

	activity.mouse_filter = (
		Control.MOUSE_FILTER_IGNORE
	)

	content.add_child(
		activity
	)

	status_label = Label.new()
	status_label.name = "Status"

	status_label.text = (
		"INITIALIZING"
	)

	status_label.horizontal_alignment = (
		HORIZONTAL_ALIGNMENT_CENTER
	)

	status_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_PRIMARY
	)

	status_label.add_theme_font_size_override(
		"font_size",
		16
	)

	content.add_child(
		status_label
	)

	detail_label = Label.new()
	detail_label.name = "Detail"

	detail_label.text = (
		"Preparing Strontium RAG"
	)

	detail_label.horizontal_alignment = (
		HORIZONTAL_ALIGNMENT_CENTER
	)

	detail_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	detail_label.add_theme_font_size_override(
		"font_size",
		13
	)

	content.add_child(
		detail_label
	)

	progress_label = Label.new()
	progress_label.name = "Progress"

	progress_label.text = ""

	progress_label.horizontal_alignment = (
		HORIZONTAL_ALIGNMENT_CENTER
	)

	progress_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	progress_label.add_theme_font_size_override(
		"font_size",
		12
	)

	content.add_child(
		progress_label
	)

	if activity != null:
		activity.play()


func _start_display_timer() -> void:
	display_timer = Timer.new()
	display_timer.name = "MinimumDisplayTimer"

	display_timer.one_shot = true
	display_timer.wait_time = maxf(
		minimum_display_time,
		0.0
	)

	add_child(
		display_timer
	)

	display_timer.timeout.connect(
		_on_minimum_display_complete
	)

	display_timer.start()


func _on_minimum_display_complete() -> void:
	minimum_time_elapsed = true

	_try_complete()


func set_initialization_stage(
	stage: String,
	detail: String = "",
	progress: float = -1.0
) -> void:
	if status_label != null:
		status_label.text = stage

	if detail_label != null:
		detail_label.text = detail

	if progress_label != null:
		if progress < 0.0:
			progress_label.text = ""
		else:
			progress_label.text = (
				"%d%%"
				% roundi(
					clampf(
						progress,
						0.0,
						100.0
					)
				)
			)


func set_status(
	status: String
) -> void:
	set_initialization_stage(
		status,
		"",
		-1.0
	)


func set_detail(
	detail: String
) -> void:
	if detail_label != null:
		detail_label.text = detail


func set_progress(
	progress: float
) -> void:
	if progress_label == null:
		return

	progress_label.text = (
		"%d%%"
		% roundi(
			clampf(
				progress,
				0.0,
				100.0
			)
		)
	)


func request_completion() -> void:
	completion_requested = true

	_try_complete()


func _try_complete() -> void:
	if transition_started:
		return

	if not completion_requested:
		return

	if not minimum_time_elapsed:
		return

	_begin_transition()


func _begin_transition() -> void:
	transition_started = true

	if activity != null:
		activity.stop()

	var tween := create_tween()

	tween.set_parallel(true)

	tween.tween_property(
		self,
		"modulate:a",
		0.0,
		fade_duration
	)

	tween.tween_property(
		content,
		"position:y",
		content.position.y - 12.0,
		fade_duration
	)

	tween.set_parallel(false)

	tween.tween_callback(
		_finish_transition
	)


func _finish_transition() -> void:
	hide()

	splash_completed.emit()
	transition_requested.emit()


func reset_splash() -> void:
	completion_requested = false
	transition_started = false
	minimum_time_elapsed = false

	modulate.a = 1.0

	content.position.y = -150.0

	show()

	if activity != null:
		activity.play()

	if display_timer != null:
		display_timer.start()


func set_glow_enabled(
	enabled: bool
) -> void:
	glow_enabled = enabled


func is_glow_enabled() -> bool:
	return glow_enabled
