class_name StrontiumWindowService
extends Node


signal window_resized(size: Vector2i)
signal fullscreen_changed(fullscreen: bool)
signal maximized_changed(maximized: bool)
signal window_state_changed(state: String)


const DEFAULT_MINIMUM_SIZE := Vector2i(960, 540)
const DEFAULT_WINDOW_SIZE := Vector2i(1280, 720)


@export var minimum_window_size: Vector2i = DEFAULT_MINIMUM_SIZE
@export var default_window_size: Vector2i = DEFAULT_WINDOW_SIZE
@export var allow_fullscreen: bool = true
@export var allow_maximize: bool = true


var initialized: bool = false

var windowed_size: Vector2i = DEFAULT_WINDOW_SIZE
var windowed_position: Vector2i = Vector2i.ZERO

var fullscreen_enabled: bool = false
var maximized_enabled: bool = false


func _ready() -> void:
	initialize()


func initialize() -> void:
	if initialized:
		return

	_configure_window()
	_connect_signals()
	_capture_initial_state()

	initialized = true

	window_state_changed.emit(
		get_window_state()
	)


func _configure_window() -> void:
	DisplayServer.window_set_min_size(
		minimum_window_size
	)

	var current_size := (
		DisplayServer.window_get_size()
	)

	if current_size.x < minimum_window_size.x:
		current_size.x = minimum_window_size.x

	if current_size.y < minimum_window_size.y:
		current_size.y = minimum_window_size.y

	if current_size.x <= 0 or current_size.y <= 0:
		current_size = default_window_size

	DisplayServer.window_set_size(
		current_size
	)


func _connect_signals() -> void:
	var viewport := get_viewport()

	if not viewport.size_changed.is_connected(
		_on_viewport_size_changed
	):
		viewport.size_changed.connect(
			_on_viewport_size_changed
	)


func _capture_initial_state() -> void:
	var mode := DisplayServer.window_get_mode()

	fullscreen_enabled = (
		mode == DisplayServer.WINDOW_MODE_FULLSCREEN
		or mode == DisplayServer.WINDOW_MODE_EXCLUSIVE_FULLSCREEN
	)

	maximized_enabled = (
		mode == DisplayServer.WINDOW_MODE_MAXIMIZED
	)

	if not fullscreen_enabled and not maximized_enabled:
		windowed_size = DisplayServer.window_get_size()
		windowed_position = DisplayServer.window_get_position()


func _on_viewport_size_changed() -> void:
	var current_size := DisplayServer.window_get_size()

	if current_size.x <= 0 or current_size.y <= 0:
		return

	if not fullscreen_enabled and not maximized_enabled:
		windowed_size = current_size

	window_resized.emit(
		current_size
	)


func set_fullscreen(
	enabled: bool
) -> void:
	if not allow_fullscreen:
		return

	if fullscreen_enabled == enabled:
		return

	if enabled:
		var current_mode := DisplayServer.window_get_mode()

		if (
			current_mode != DisplayServer.WINDOW_MODE_FULLSCREEN
			and current_mode != DisplayServer.WINDOW_MODE_EXCLUSIVE_FULLSCREEN
			and current_mode != DisplayServer.WINDOW_MODE_MAXIMIZED
		):
			windowed_size = DisplayServer.window_get_size()
			windowed_position = DisplayServer.window_get_position()

		DisplayServer.window_set_mode(
			DisplayServer.WINDOW_MODE_FULLSCREEN
		)

		fullscreen_enabled = true
		maximized_enabled = false
	else:
		DisplayServer.window_set_mode(
			DisplayServer.WINDOW_MODE_WINDOWED
		)

		DisplayServer.window_set_size(
			windowed_size
		)

		DisplayServer.window_set_position(
			windowed_position
		)

		fullscreen_enabled = false

	fullscreen_changed.emit(
		fullscreen_enabled
	)

	window_state_changed.emit(
		get_window_state()
	)


func toggle_fullscreen() -> void:
	set_fullscreen(
		not fullscreen_enabled
	)


func is_fullscreen() -> bool:
	return fullscreen_enabled


func set_maximized(
	enabled: bool
) -> void:
	if not allow_maximize:
		return

	if maximized_enabled == enabled:
		return

	if enabled:
		if fullscreen_enabled:
			return

		windowed_size = DisplayServer.window_get_size()
		windowed_position = DisplayServer.window_get_position()

		DisplayServer.window_set_mode(
			DisplayServer.WINDOW_MODE_MAXIMIZED
		)

		maximized_enabled = true
	else:
		DisplayServer.window_set_mode(
			DisplayServer.WINDOW_MODE_WINDOWED
		)

		DisplayServer.window_set_size(
			windowed_size
		)

		DisplayServer.window_set_position(
			windowed_position
		)

		maximized_enabled = false

	maximized_changed.emit(
		maximized_enabled
	)

	window_state_changed.emit(
		get_window_state()
	)


func toggle_maximized() -> void:
	set_maximized(
		not maximized_enabled
	)


func is_maximized() -> bool:
	return maximized_enabled


func restore_window() -> void:
	if fullscreen_enabled:
		set_fullscreen(false)
		return

	if maximized_enabled:
		set_maximized(false)
		return

	DisplayServer.window_set_size(
		windowed_size
	)

	DisplayServer.window_set_position(
		windowed_position
	)

	window_state_changed.emit(
		get_window_state()
	)


func set_window_size(
	size: Vector2i
) -> void:
	var clamped_size := Vector2i(
		maxi(
			size.x,
			minimum_window_size.x
		),
		maxi(
			size.y,
			minimum_window_size.y
		)
	)

	windowed_size = clamped_size

	if fullscreen_enabled or maximized_enabled:
		return

	DisplayServer.window_set_size(
		clamped_size
	)

	window_resized.emit(
		clamped_size
	)


func get_window_size() -> Vector2i:
	return DisplayServer.window_get_size()


func get_windowed_size() -> Vector2i:
	return windowed_size


func set_minimum_window_size(
	size: Vector2i
) -> void:
	minimum_window_size = Vector2i(
		maxi(size.x, 1),
		maxi(size.y, 1)
	)

	DisplayServer.window_set_min_size(
		minimum_window_size
	)


func get_minimum_window_size() -> Vector2i:
	return minimum_window_size


func get_window_state() -> String:
	if fullscreen_enabled:
		return "FULLSCREEN"

	if maximized_enabled:
		return "MAXIMIZED"

	return "WINDOWED"


func is_windowed() -> bool:
	return not fullscreen_enabled and not maximized_enabled


func refresh_state() -> void:
	var mode := DisplayServer.window_get_mode()

	var previous_fullscreen := fullscreen_enabled
	var previous_maximized := maximized_enabled

	fullscreen_enabled = (
		mode == DisplayServer.WINDOW_MODE_FULLSCREEN
		or mode == DisplayServer.WINDOW_MODE_EXCLUSIVE_FULLSCREEN
	)

	maximized_enabled = (
		mode == DisplayServer.WINDOW_MODE_MAXIMIZED
	)

	if (
		previous_fullscreen
		!= fullscreen_enabled
	):
		fullscreen_changed.emit(
			fullscreen_enabled
		)

	if (
		previous_maximized
		!= maximized_enabled
	):
		maximized_changed.emit(
			maximized_enabled
		)

	window_state_changed.emit(
		get_window_state()
	)
