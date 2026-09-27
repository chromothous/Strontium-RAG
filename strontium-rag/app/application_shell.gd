class_name StrontiumApplicationShell
extends Control


const HEADER_HEIGHT: float = 72.0
const FOOTER_HEIGHT: float = 40.0

const NAV_WIDTH_MIN: float = 200.0
const NAV_WIDTH_DEFAULT: float = 240.0
const NAV_WIDTH_MAX: float = 280.0

const MINIMUM_WINDOW_WIDTH: int = 960
const MINIMUM_WINDOW_HEIGHT: int = 540

const WINDOW_TITLE: String = "Strontium RAG"


var window_service: StrontiumWindowService
var startup_service: StrontiumStartupService
var splash: StrontiumSplash

var background_root: Control
var header_root: Control
var navigation_root: Control
var content_root: Control
var overlay_root: Control
var status_root: Control
var modal_root: Control

var current_shell_size: Vector2 = Vector2.ZERO
var current_navigation_width: float = NAV_WIDTH_DEFAULT


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_STOP

	_resolve_shell_nodes()
	_initialize_window_service()
	_initialize_startup_service()

	_configure_window()
	_connect_window_signals()
	_connect_startup_signals()

	_apply_shell_layout()
	_start_splash()


func _resolve_shell_nodes() -> void:
	background_root = get_node_or_null("BackgroundRoot") as Control
	header_root = get_node_or_null("HeaderRoot") as Control
	navigation_root = get_node_or_null("NavigationRoot") as Control
	content_root = get_node_or_null("ContentRoot") as Control
	overlay_root = get_node_or_null("OverlayRoot") as Control
	status_root = get_node_or_null("StatusRoot") as Control
	modal_root = get_node_or_null("ModalRoot") as Control


func _initialize_window_service() -> void:
	window_service = get_node_or_null("WindowService") as StrontiumWindowService

	if window_service == null:
		window_service = StrontiumWindowService.new()
		window_service.name = "WindowService"
		add_child(window_service)

	window_service.minimum_window_size = Vector2i(
		MINIMUM_WINDOW_WIDTH,
		MINIMUM_WINDOW_HEIGHT
	)


func _initialize_startup_service() -> void:
	startup_service = get_node_or_null("StartupService") as StrontiumStartupService

	if startup_service == null:
		startup_service = StrontiumStartupService.new()
		startup_service.name = "StartupService"
		add_child(startup_service)


func _configure_window() -> void:
	DisplayServer.window_set_title(WINDOW_TITLE)

	window_service.set_minimum_window_size(
		Vector2i(
			MINIMUM_WINDOW_WIDTH,
			MINIMUM_WINDOW_HEIGHT
		)
	)


func _connect_window_signals() -> void:
	if window_service == null:
		return

	if not window_service.window_resized.is_connected(_on_window_resized):
		window_service.window_resized.connect(_on_window_resized)

	if not window_service.fullscreen_changed.is_connected(_on_fullscreen_changed):
		window_service.fullscreen_changed.connect(_on_fullscreen_changed)


func _connect_startup_signals() -> void:
	if startup_service == null:
		return

	if not startup_service.stage_changed.is_connected(_on_startup_stage_changed):
		startup_service.stage_changed.connect(_on_startup_stage_changed)

	if not startup_service.startup_completed.is_connected(_on_startup_completed):
		startup_service.startup_completed.connect(_on_startup_completed)

	if not startup_service.startup_failed.is_connected(_on_startup_failed):
		startup_service.startup_failed.connect(_on_startup_failed)


func _start_splash() -> void:
	splash = StrontiumSplash.new()
	splash.name = "Splash"
	splash.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	splash.z_index = 1000

	add_child(splash)

	if not splash.splash_completed.is_connected(_on_splash_completed):
		splash.splash_completed.connect(_on_splash_completed)

	_hide_application_shell()

	startup_service.initialize()


func _on_startup_stage_changed(
	_stage: StrontiumStartupService.StartupStage,
	stage_name: String,
	detail: String,
	progress: float
) -> void:
	if splash == null:
		return

	if not is_instance_valid(splash):
		return

	splash.set_initialization_stage(
		stage_name,
		detail,
		progress
	)


func _on_startup_completed() -> void:
	if splash == null:
		return

	if not is_instance_valid(splash):
		return

	splash.set_initialization_stage(
		"READY",
		"Application startup pipeline prepared",
		100.0
	)

	splash.request_completion()


func _on_startup_failed(
	_stage: StrontiumStartupService.StartupStage,
	detail: String
) -> void:
	if splash == null:
		return

	if not is_instance_valid(splash):
		return

	splash.set_initialization_stage(
		"STARTUP FAILED",
		detail,
		100.0
	)


func _hide_application_shell() -> void:
	if background_root != null:
		background_root.hide()

	if header_root != null:
		header_root.hide()

	if navigation_root != null:
		navigation_root.hide()

	if content_root != null:
		content_root.hide()

	if overlay_root != null:
		overlay_root.hide()

	if status_root != null:
		status_root.hide()

	if modal_root != null:
		modal_root.hide()


func _show_application_shell() -> void:
	if background_root != null:
		background_root.show()

	if header_root != null:
		header_root.show()

	if navigation_root != null:
		navigation_root.show()

	if content_root != null:
		content_root.show()

	if overlay_root != null:
		overlay_root.show()

	if status_root != null:
		status_root.show()

	if modal_root != null:
		modal_root.show()


func _on_splash_completed() -> void:
	_show_application_shell()
	_apply_shell_layout()


func _on_window_resized(_size: Vector2i) -> void:
	_apply_shell_layout()


func _on_fullscreen_changed(_fullscreen: bool) -> void:
	_apply_shell_layout()


func _apply_shell_layout() -> void:
	var viewport_size: Vector2 = get_viewport_rect().size

	if viewport_size.x <= 0.0 or viewport_size.y <= 0.0:
		return

	current_shell_size = viewport_size
	current_navigation_width = _calculate_navigation_width(
		viewport_size.x
	)

	_set_full_rect(background_root)

	_set_rect(
		header_root,
		Vector2(0.0, 0.0),
		Vector2(
			viewport_size.x,
			HEADER_HEIGHT
		)
	)

	var content_height: float = maxf(
		0.0,
		viewport_size.y - HEADER_HEIGHT - FOOTER_HEIGHT
	)

	_set_rect(
		navigation_root,
		Vector2(
			0.0,
			HEADER_HEIGHT
		),
		Vector2(
			current_navigation_width,
			content_height
		)
	)

	_set_rect(
		content_root,
		Vector2(
			current_navigation_width,
			HEADER_HEIGHT
		),
		Vector2(
			maxf(
				0.0,
				viewport_size.x - current_navigation_width
			),
			content_height
		)
	)

	_set_full_rect(overlay_root)

	_set_rect(
		status_root,
		Vector2(
			0.0,
			maxf(
				0.0,
				viewport_size.y - FOOTER_HEIGHT
			)
		),
		Vector2(
			viewport_size.x,
			FOOTER_HEIGHT
		)
	)

	_set_full_rect(modal_root)

	if splash != null and is_instance_valid(splash):
		splash.set_anchors_and_offsets_preset(
			Control.PRESET_FULL_RECT
		)


func _calculate_navigation_width(window_width: float) -> float:
	if window_width < 1100.0:
		return NAV_WIDTH_MIN

	if window_width > 1500.0:
		return NAV_WIDTH_MAX

	var interpolation: float = inverse_lerp(
		1100.0,
		1500.0,
		window_width
	)

	return lerpf(
		NAV_WIDTH_DEFAULT,
		NAV_WIDTH_MAX,
		interpolation
	)


func _set_full_rect(control: Control) -> void:
	if control == null:
		return

	control.position = Vector2.ZERO
	control.size = current_shell_size


func _set_rect(
	control: Control,
	position: Vector2,
	size: Vector2
) -> void:
	if control == null:
		return

	control.position = position
	control.size = size


func toggle_fullscreen() -> void:
	if window_service == null:
		return

	window_service.toggle_fullscreen()


func is_fullscreen() -> bool:
	if window_service == null:
		return false

	return window_service.is_fullscreen()


func toggle_maximized() -> void:
	if window_service == null:
		return

	window_service.toggle_maximized()


func restore_window() -> void:
	if window_service == null:
		return

	window_service.restore_window()


func set_window_size(size: Vector2i) -> void:
	if window_service == null:
		return

	window_service.set_window_size(size)


func get_window_size() -> Vector2i:
	if window_service == null:
		return Vector2i.ZERO

	return window_service.get_window_size()


func get_shell_size() -> Vector2:
	return current_shell_size


func get_navigation_width() -> float:
	return current_navigation_width


func get_startup_state() -> Dictionary:
	if startup_service == null:
		return {}

	return startup_service.get_startup_state()


func _unhandled_key_input(event: InputEvent) -> void:
	var key_event: InputEventKey = event as InputEventKey

	if key_event == null:
		return

	if not key_event.pressed:
		return

	if key_event.echo:
		return

	if key_event.keycode == KEY_F11:
		toggle_fullscreen()
		get_viewport().set_input_as_handled()
