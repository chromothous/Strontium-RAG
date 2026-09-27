class_name StrontiumIcon
extends Control


enum IconType {
	HOME,
	DATABASE,
	DOCUMENT,
	CHAT,
	SEARCH,
	SETTINGS,
	SHIELD,
	ACTIVITY,
	ERROR,
	INFO,
	WARNING,
	CHECK,
	ARROW_RIGHT,
	ARROW_LEFT,
	PLUS,
	CLOSE
}


@export var icon_type: IconType = IconType.HOME
@export var icon_size: float = 20.0
@export var stroke_width: float = 1.75
@export var icon_color: Color = StrontiumTokens.TEXT_SECONDARY
@export var glow_enabled: bool = false
@export var glow_strength: float = 0.30


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE

	size_flags_vertical = Control.SIZE_SHRINK_CENTER

	custom_minimum_size = Vector2(
		icon_size,
		icon_size
	)

	queue_redraw()


func _draw() -> void:
	var drawing_size := Vector2(
		icon_size,
		icon_size
	)

	var drawing_origin := (
		size - drawing_size
	) / 2.0

	draw_set_transform(
		drawing_origin,
		0.0,
		Vector2.ONE
	)

	if glow_enabled:
		_draw_glow()

	_draw_icon(
		icon_color,
		stroke_width
	)

	draw_set_transform(
		Vector2.ZERO,
		0.0,
		Vector2.ONE
	)


func _draw_glow() -> void:
	var original_width := stroke_width

	var glow_color := icon_color
	glow_color.a = clampf(
		glow_strength,
		0.0,
		1.0
	)

	stroke_width = maxf(
		original_width * 2.75,
		original_width + 2.0
	)

	_draw_icon(
		glow_color,
		stroke_width
	)

	stroke_width = original_width


func _draw_icon(
	color: Color,
	width: float
) -> void:
	var original_width := stroke_width

	stroke_width = width

	match icon_type:
		IconType.HOME:
			_draw_home(color)

		IconType.DATABASE:
			_draw_database(color)

		IconType.DOCUMENT:
			_draw_document(color)

		IconType.CHAT:
			_draw_chat(color)

		IconType.SEARCH:
			_draw_search(color)

		IconType.SETTINGS:
			_draw_settings(color)

		IconType.SHIELD:
			_draw_shield(color)

		IconType.ACTIVITY:
			_draw_activity(color)

		IconType.ERROR:
			_draw_error(color)

		IconType.INFO:
			_draw_info(color)

		IconType.WARNING:
			_draw_warning(color)

		IconType.CHECK:
			_draw_check(color)

		IconType.ARROW_RIGHT:
			_draw_arrow_right(color)

		IconType.ARROW_LEFT:
			_draw_arrow_left(color)

		IconType.PLUS:
			_draw_plus(color)

		IconType.CLOSE:
			_draw_close(color)

	stroke_width = original_width


func _draw_home(color: Color) -> void:
	var left := icon_size * 0.22
	var right := icon_size * 0.78
	var top := icon_size * 0.42
	var bottom := icon_size * 0.82
	var peak := icon_size * 0.16

	draw_line(
		Vector2(left, top),
		Vector2(icon_size * 0.50, peak),
		color,
		stroke_width,
		true
	)

	draw_line(
		Vector2(icon_size * 0.50, peak),
		Vector2(right, top),
		color,
		stroke_width,
		true
	)

	draw_line(
		Vector2(left, top),
		Vector2(left, bottom),
		color,
		stroke_width,
		true
	)

	draw_line(
		Vector2(right, top),
		Vector2(right, bottom),
		color,
		stroke_width,
		true
	)

	draw_line(
		Vector2(left, bottom),
		Vector2(right, bottom),
		color,
		stroke_width,
		true
	)

	draw_line(
		Vector2(icon_size * 0.43, bottom),
		Vector2(icon_size * 0.43, icon_size * 0.60),
		color,
		stroke_width,
		true
	)

	draw_line(
		Vector2(icon_size * 0.57, bottom),
		Vector2(icon_size * 0.57, icon_size * 0.60),
		color,
		stroke_width,
		true
	)


func _draw_database(color: Color) -> void:
	var center_x := icon_size * 0.50
	var top_y := icon_size * 0.22
	var bottom_y := icon_size * 0.80
	var radius_x := icon_size * 0.28
	var radius_y := icon_size * 0.10

	_draw_ellipse(
		Vector2(center_x, top_y),
		radius_x,
		radius_y,
		color
	)

	draw_line(
		Vector2(
			center_x - radius_x,
			top_y
		),
		Vector2(
			center_x - radius_x,
			bottom_y
		),
		color,
		stroke_width,
		true
	)

	draw_line(
		Vector2(
			center_x + radius_x,
			top_y
		),
		Vector2(
			center_x + radius_x,
			bottom_y
		),
		color,
		stroke_width,
		true
	)

	_draw_ellipse(
		Vector2(center_x, icon_size * 0.49),
		radius_x,
		radius_y,
		color
	)

	_draw_ellipse(
		Vector2(center_x, bottom_y),
		radius_x,
		radius_y,
		color
	)


func _draw_document(color: Color) -> void:
	var left := icon_size * 0.24
	var right := icon_size * 0.76
	var top := icon_size * 0.16
	var bottom := icon_size * 0.84
	var fold_x := icon_size * 0.58
	var fold_y := icon_size * 0.34

	draw_line(
		Vector2(left, top),
		Vector2(fold_x, top),
		color,
		stroke_width,
		true
	)

	draw_line(
		Vector2(fold_x, top),
		Vector2(right, fold_y),
		color,
		stroke_width,
		true
	)

	draw_line(
		Vector2(right, fold_y),
		Vector2(right, bottom),
		color,
		stroke_width,
		true
	)

	draw_line(
		Vector2(right, bottom),
		Vector2(left, bottom),
		color,
		stroke_width,
		true
	)

	draw_line(
		Vector2(left, bottom),
		Vector2(left, top),
		color,
		stroke_width,
		true
	)

	draw_line(
		Vector2(fold_x, top),
		Vector2(fold_x, fold_y),
		color,
		stroke_width,
		true
	)

	draw_line(
		Vector2(fold_x, fold_y),
		Vector2(right, fold_y),
		color,
		stroke_width,
		true
	)

	draw_line(
		Vector2(icon_size * 0.34, icon_size * 0.52),
		Vector2(icon_size * 0.66, icon_size * 0.52),
		color,
		stroke_width,
		true
	)

	draw_line(
		Vector2(icon_size * 0.34, icon_size * 0.66),
		Vector2(icon_size * 0.60, icon_size * 0.66),
		color,
		stroke_width,
		true
	)


func _draw_chat(color: Color) -> void:
	var left := icon_size * 0.18
	var right := icon_size * 0.82
	var top := icon_size * 0.20
	var bottom := icon_size * 0.68

	draw_rect(
		Rect2(
			left,
			top,
			right - left,
			bottom - top
		),
		color,
		false,
		stroke_width
	)

	draw_line(
		Vector2(
			icon_size * 0.38,
			bottom
		),
		Vector2(
			icon_size * 0.30,
			icon_size * 0.84
		),
		color,
		stroke_width,
		true
	)

	draw_line(
		Vector2(
			icon_size * 0.30,
			icon_size * 0.84
		),
		Vector2(
			icon_size * 0.48,
			bottom
		),
		color,
		stroke_width,
		true
	)


func _draw_search(color: Color) -> void:
	var center := Vector2(
		icon_size * 0.43,
		icon_size * 0.43
	)

	draw_arc(
		center,
		icon_size * 0.24,
		0.0,
		TAU,
		32,
		color,
		stroke_width,
		true
	)

	draw_line(
		Vector2(
			icon_size * 0.60,
			icon_size * 0.60
		),
		Vector2(
			icon_size * 0.82,
			icon_size * 0.82
		),
		color,
		stroke_width,
		true
	)


func _draw_settings(color: Color) -> void:
	var center := Vector2(
		icon_size * 0.50,
		icon_size * 0.50
	)

	draw_circle(
		center,
		icon_size * 0.25,
		color,
		false,
		stroke_width,
		true
	)

	draw_circle(
		center,
		icon_size * 0.08,
		color,
		false,
		stroke_width,
		true
	)

	var inner_radius := icon_size * 0.28
	var outer_radius := icon_size * 0.42

	for index in range(8):
		var angle := (
			float(index) / 8.0
		) * TAU

		var start := center + Vector2(
			cos(angle),
			sin(angle)
		) * inner_radius

		var end := center + Vector2(
			cos(angle),
			sin(angle)
		) * outer_radius

		draw_line(
			start,
			end,
			color,
			stroke_width,
			true
		)


func _draw_shield(color: Color) -> void:
	var top := Vector2(
		icon_size * 0.50,
		icon_size * 0.14
	)

	var left := Vector2(
		icon_size * 0.22,
		icon_size * 0.28
	)

	var right := Vector2(
		icon_size * 0.78,
		icon_size * 0.28
	)

	var bottom := Vector2(
		icon_size * 0.50,
		icon_size * 0.86
	)

	var points := PackedVector2Array([
		top,
		right,
		Vector2(
			icon_size * 0.72,
			icon_size * 0.62
		),
		bottom,
		Vector2(
			icon_size * 0.28,
			icon_size * 0.62
		),
		left
	])

	draw_polyline(
		points,
		color,
		stroke_width,
		true
	)

	draw_line(
		points[points.size() - 1],
		points[0],
		color,
		stroke_width,
		true
	)


func _draw_activity(color: Color) -> void:
	var points := PackedVector2Array([
		Vector2(
			icon_size * 0.12,
			icon_size * 0.56
		),
		Vector2(
			icon_size * 0.30,
			icon_size * 0.56
		),
		Vector2(
			icon_size * 0.40,
			icon_size * 0.30
		),
		Vector2(
			icon_size * 0.56,
			icon_size * 0.76
		),
		Vector2(
			icon_size * 0.68,
			icon_size * 0.46
		),
		Vector2(
			icon_size * 0.88,
			icon_size * 0.46
		)
	])

	draw_polyline(
		points,
		color,
		stroke_width,
		true
	)


func _draw_error(color: Color) -> void:
	var center := Vector2(
		icon_size * 0.50,
		icon_size * 0.50
	)

	draw_circle(
		center,
		icon_size * 0.34,
		color,
		false,
		stroke_width,
		true
	)

	draw_line(
		Vector2(
			icon_size * 0.50,
			icon_size * 0.30
		),
		Vector2(
			icon_size * 0.50,
			icon_size * 0.56
		),
		color,
		stroke_width,
		true
	)

	draw_circle(
		Vector2(
			icon_size * 0.50,
			icon_size * 0.68
		),
		stroke_width * 0.55,
		color
	)


func _draw_info(color: Color) -> void:
	var center := Vector2(
		icon_size * 0.50,
		icon_size * 0.50
	)

	draw_circle(
		center,
		icon_size * 0.34,
		color,
		false,
		stroke_width,
		true
	)

	draw_circle(
		Vector2(
			icon_size * 0.50,
			icon_size * 0.34
		),
		stroke_width * 0.55,
		color
	)

	draw_line(
		Vector2(
			icon_size * 0.50,
			icon_size * 0.45
		),
		Vector2(
			icon_size * 0.50,
			icon_size * 0.70
		),
		color,
		stroke_width,
		true
	)


func _draw_warning(color: Color) -> void:
	var top := Vector2(
		icon_size * 0.50,
		icon_size * 0.16
	)

	var left := Vector2(
		icon_size * 0.18,
		icon_size * 0.82
	)

	var right := Vector2(
		icon_size * 0.82,
		icon_size * 0.82
	)

	draw_polyline(
		PackedVector2Array([
			top,
			right,
			left,
			top
		]),
		color,
		stroke_width,
		true
	)

	draw_line(
		Vector2(
			icon_size * 0.50,
			icon_size * 0.38
		),
		Vector2(
			icon_size * 0.50,
			icon_size * 0.62
		),
		color,
		stroke_width,
		true
	)

	draw_circle(
		Vector2(
			icon_size * 0.50,
			icon_size * 0.70
		),
		stroke_width * 0.55,
		color
	)


func _draw_check(color: Color) -> void:
	draw_polyline(
		PackedVector2Array([
			Vector2(
				icon_size * 0.20,
				icon_size * 0.52
			),
			Vector2(
				icon_size * 0.42,
				icon_size * 0.74
			),
			Vector2(
				icon_size * 0.80,
				icon_size * 0.28
			)
		]),
		color,
		stroke_width,
		true
	)


func _draw_arrow_right(color: Color) -> void:
	draw_line(
		Vector2(
			icon_size * 0.18,
			icon_size * 0.50
		),
		Vector2(
			icon_size * 0.76,
			icon_size * 0.50
		),
		color,
		stroke_width,
		true
	)

	draw_line(
		Vector2(
			icon_size * 0.56,
			icon_size * 0.30
		),
		Vector2(
			icon_size * 0.80,
			icon_size * 0.50
		),
		color,
		stroke_width,
		true
	)

	draw_line(
		Vector2(
			icon_size * 0.80,
			icon_size * 0.50
		),
		Vector2(
			icon_size * 0.56,
			icon_size * 0.70
		),
		color,
		stroke_width,
		true
	)


func _draw_arrow_left(color: Color) -> void:
	draw_line(
		Vector2(
			icon_size * 0.82,
			icon_size * 0.50
		),
		Vector2(
			icon_size * 0.24,
			icon_size * 0.50
		),
		color,
		stroke_width,
		true
	)

	draw_line(
		Vector2(
			icon_size * 0.44,
			icon_size * 0.30
		),
		Vector2(
			icon_size * 0.20,
			icon_size * 0.50
		),
		color,
		stroke_width,
		true
	)

	draw_line(
		Vector2(
			icon_size * 0.20,
			icon_size * 0.50
		),
		Vector2(
			icon_size * 0.44,
			icon_size * 0.70
		),
		color,
		stroke_width,
		true
	)


func _draw_plus(color: Color) -> void:
	draw_line(
		Vector2(
			icon_size * 0.50,
			icon_size * 0.20
		),
		Vector2(
			icon_size * 0.50,
			icon_size * 0.80
		),
		color,
		stroke_width,
		true
	)

	draw_line(
		Vector2(
			icon_size * 0.20,
			icon_size * 0.50
		),
		Vector2(
			icon_size * 0.80,
			icon_size * 0.50
		),
		color,
		stroke_width,
		true
	)


func _draw_close(color: Color) -> void:
	draw_line(
		Vector2(
			icon_size * 0.24,
			icon_size * 0.24
		),
		Vector2(
			icon_size * 0.76,
			icon_size * 0.76
		),
		color,
		stroke_width,
		true
	)

	draw_line(
		Vector2(
			icon_size * 0.76,
			icon_size * 0.24
		),
		Vector2(
			icon_size * 0.24,
			icon_size * 0.76
		),
		color,
		stroke_width,
		true
	)


func _draw_ellipse(
	center: Vector2,
	radius_x: float,
	radius_y: float,
	color: Color
) -> void:
	var points := PackedVector2Array()
	var point_count := 32

	for index in range(point_count + 1):
		var angle := (
			float(index) / float(point_count)
		) * TAU

		points.append(
			center
			+ Vector2(
				cos(angle) * radius_x,
				sin(angle) * radius_y
			)
		)

	draw_polyline(
		points,
		color,
		stroke_width,
		true
	)


func set_icon(
	new_icon_type: IconType
) -> void:
	icon_type = new_icon_type
	queue_redraw()


func get_icon() -> IconType:
	return icon_type


func set_icon_color(
	color: Color
) -> void:
	icon_color = color
	queue_redraw()


func get_icon_color() -> Color:
	return icon_color


func set_icon_size(
	new_size: float
) -> void:
	icon_size = maxf(
		new_size,
		1.0
	)

	custom_minimum_size = Vector2(
		icon_size,
		icon_size
	)

	queue_redraw()


func set_stroke_width(
	width: float
) -> void:
	stroke_width = maxf(
		width,
		0.5
	)

	queue_redraw()


func set_glow(
	enabled: bool,
	strength: float = 0.30
) -> void:
	glow_enabled = enabled
	glow_strength = clampf(
		strength,
		0.0,
		1.0
	)

	queue_redraw()


func is_glow_enabled() -> bool:
	return glow_enabled


func get_glow_strength() -> float:
	return glow_strength


func get_icon_name() -> String:
	return IconType.keys()[icon_type]
