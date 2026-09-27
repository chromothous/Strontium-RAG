class_name StrontiumActivityIndicator
extends Control


@export var dot_count: int = 3
@export var dot_radius: float = 4.0
@export var dot_spacing: float = 10.0
@export var animation_speed: float = 0.75
@export var indicator_color: Color = StrontiumTokens.ACCENT_PRIMARY


var animation_time: float = 0.0
var playing: bool = true


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_update_minimum_size()
	queue_redraw()


func _process(delta: float) -> void:
	if not playing:
		return

	animation_time = fmod(
		animation_time + delta,
		animation_speed
	)

	queue_redraw()


func _draw() -> void:
	if dot_count <= 0:
		return

	var diameter: float = dot_radius * 2.0
	var total_width: float = (
		diameter * float(dot_count)
		+ dot_spacing * float(dot_count - 1)
	)

	var start_x: float = (
		(size.x - total_width) / 2.0
		+ dot_radius
	)

	var center_y: float = size.y / 2.0

	for index in range(dot_count):
		var phase: float = (
			animation_time / animation_speed
			+ float(index) / float(dot_count)
		)

		var pulse: float = (
			sin(phase * TAU) + 1.0
		) / 2.0

		var alpha: float = lerp(
			0.20,
			1.0,
			pulse
		)

		var color := indicator_color
		color.a = alpha

		var x: float = (
			start_x
			+ float(index)
			* (diameter + dot_spacing)
		)

		draw_circle(
			Vector2(x, center_y),
			dot_radius,
			color
		)


func play() -> void:
	playing = true
	queue_redraw()


func stop() -> void:
	playing = false
	queue_redraw()


func set_indicator_color(color: Color) -> void:
	indicator_color = color
	queue_redraw()


func set_animation_speed(speed: float) -> void:
	animation_speed = maxf(
		speed,
		0.05
	)

	animation_time = 0.0
	queue_redraw()


func _update_minimum_size() -> void:
	if dot_count <= 0:
		custom_minimum_size = Vector2.ZERO
		return

	var diameter: float = dot_radius * 2.0
	var total_width: float = (
		diameter * float(dot_count)
		+ dot_spacing * float(dot_count - 1)
	)

	custom_minimum_size = Vector2(
		total_width,
		diameter
	)
