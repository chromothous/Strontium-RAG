class_name StrontiumThemeService
extends Node


signal theme_applied
signal theme_refresh_requested


var root_control: Control
var current_theme: Theme
var initialized: bool = false


func configure(
	target_root: Control
) -> void:
	if target_root == null:
		push_error(
            "StrontiumThemeService requires "
			+ "a valid root Control."
		)
		return

	root_control = target_root


func initialize() -> void:
	if initialized:
		return

	if root_control == null:
		push_error(
            "StrontiumThemeService cannot initialize "
			+ "without a configured root Control."
		)
		return

	_build_and_apply_theme()

	initialized = true
	theme_applied.emit()


func refresh() -> void:
	if root_control == null:
		push_error(
            "StrontiumThemeService cannot refresh "
			+ "without a configured root Control."
		)
		return

	_build_and_apply_theme()
	theme_refresh_requested.emit()


func is_initialized() -> bool:
	return initialized


func get_theme() -> Theme:
	return current_theme


func get_root_control() -> Control:
	return root_control


func _build_and_apply_theme() -> void:
	current_theme = StrontiumTheme.build()

	root_control.theme = current_theme
