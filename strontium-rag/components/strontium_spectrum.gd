class_name StrontiumSpectrum
extends Control


@export var animated: bool = true
@export var animation_speed: float = 0.045
@export var intensity: float = 0.85
@export var line_height: float = 2.0


var spectrum_colors: Array[Color] = [
	StrontiumTokens.SPECTRUM_RED,
	StrontiumTokens.SPECTRUM_ORANGE,
	StrontiumTokens.SPECTRUM_YELLOW,
	StrontiumTokens.SPECTRUM_GREEN,
	StrontiumTokens.SPECTRUM_CYAN,
	StrontiumTokens.SPECTRUM_BLUE,
	StrontiumTokens.SPECTRUM_VIOLET,
	StrontiumTokens.SPECTRUM_MAGENTA
]

var spectrum_offset: float = 0.0


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	custom_minimum_size = Vector2(0, line_height)
	queue_redraw()


func _process(delta: float) -> void:
	if not animated:
		return

	spectrum_offset = fmod(
		spectrum_offset + animation_speed * delta,
		1.0
	)

	queue_redraw()


func _draw() -> void:
	var width: float = size.x

	if width <= 0.0:
		return

	var segment_count: int = maxi(
		32,
		int(width / 4.0)
	)

	var segment_width: float = (
		width / float(segment_count)
	)

	for index in range(segment_count):
		var start_ratio: float = (
			float(index) / float(segment_count)
		)

		var spectrum_position: float = fmod(
			start_ratio + spectrum_offset,
			1.0
		)

		var color: Color = _sample_spectrum(
			spectrum_position
		)

		color.a = intensity

		draw_rect(
			Rect2(
				index * segment_width,
				0.0,
				segment_width + 1.0,
				line_height
			),
			color
		)


func _sample_spectrum(position: float) -> Color:
	var color_count: int = spectrum_colors.size()

	if color_count == 0:
		return StrontiumTokens.ACCENT_PRIMARY

	var scaled_position: float = (
		position * float(color_count)
	)

	var index: int = (
		int(floor(scaled_position)) % color_count
	)

	var next_index: int = (
		(index + 1) % color_count
	)

	var interpolation: float = fmod(
		scaled_position,
		1.0
	)

	return spectrum_colors[index].lerp(
		spectrum_colors[next_index],
		interpolation
	)


func set_animated(value: bool) -> void:
	animated = value

	if not animated:
		spectrum_offset = 0.0

	queue_redraw()


func set_intensity(value: float) -> void:
	intensity = clampf(
		value,
		0.0,
		1.0
	)

	queue_redraw()


func set_animation_speed(value: float) -> void:
	animation_speed = maxf(
		value,
		0.0
	)


func set_line_height(value: float) -> void:
	line_height = maxf(
		value,
		1.0
	)

	custom_minimum_size.y = line_height
	queue_redraw()
