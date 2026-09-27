class_name StrontiumTheme
extends RefCounted


static func build() -> Theme:
	var theme := Theme.new()

	_configure_defaults(theme)
	_configure_buttons(theme)
	_configure_labels(theme)
	_configure_panels(theme)
	_configure_line_edit(theme)
	_configure_tabs(theme)
	_configure_sliders(theme)
	_configure_progress_bars(theme)
	_configure_popups(theme)
	_configure_menu_buttons(theme)

	return theme


static func _configure_defaults(
	theme: Theme
) -> void:
	theme.default_font_size = (
		StrontiumTokens.FONT_SIZE_BODY
	)


static func _configure_buttons(
	theme: Theme
) -> void:
	theme.set_font_size(
		"font_size",
		"Button",
		StrontiumTokens.FONT_SIZE_BODY
	)

	theme.set_color(
		"font_color",
		"Button",
		StrontiumTokens.TEXT_SECONDARY
	)

	theme.set_color(
		"font_hover_color",
		"Button",
		StrontiumTokens.ACCENT_PRIMARY
	)

	theme.set_color(
		"font_pressed_color",
		"Button",
		StrontiumTokens.TEXT_PRIMARY
	)

	theme.set_color(
		"font_focus_color",
		"Button",
		StrontiumTokens.TEXT_PRIMARY
	)

	theme.set_color(
		"font_disabled_color",
		"Button",
		StrontiumTokens.INTERACTION_DISABLED
	)

	theme.set_stylebox(
		"normal",
		"Button",
		_create_style(
			StrontiumTokens.SURFACE_PRIMARY,
			StrontiumTokens.BORDER_SUBTLE,
			1
		)
	)

	theme.set_stylebox(
		"hover",
		"Button",
		_create_style(
			StrontiumTokens.SURFACE_ELEVATED,
			StrontiumTokens.ACCENT_PRIMARY,
			1
		)
	)

	theme.set_stylebox(
		"pressed",
		"Button",
		_create_style(
			StrontiumTokens.INTERACTION_ACTIVE,
			StrontiumTokens.ACCENT_PRIMARY,
			2
		)
	)

	theme.set_stylebox(
		"focus",
		"Button",
		_create_style(
			StrontiumTokens.SURFACE_ELEVATED,
			StrontiumTokens.ACCENT_SECONDARY,
			1
		)
	)

	theme.set_stylebox(
		"disabled",
		"Button",
		_create_style(
			StrontiumTokens.SURFACE_PRIMARY,
			StrontiumTokens.INTERACTION_DISABLED,
			1
		)
	)


static func _configure_labels(
	theme: Theme
) -> void:
	theme.set_font_size(
		"font_size",
		"Label",
		StrontiumTokens.FONT_SIZE_BODY
	)

	theme.set_color(
		"font_color",
		"Label",
		StrontiumTokens.TEXT_PRIMARY
	)


static func _configure_panels(
	theme: Theme
) -> void:
	theme.set_stylebox(
		"panel",
		"Panel",
		_create_style(
			StrontiumTokens.SURFACE_PRIMARY,
			StrontiumTokens.BORDER_SUBTLE,
			1
		)
	)

	theme.set_stylebox(
		"panel",
		"PanelContainer",
		_create_style(
			StrontiumTokens.SURFACE_PRIMARY,
			StrontiumTokens.BORDER_SUBTLE,
			1
		)
	)

	theme.set_stylebox(
		"panel",
		"PopupPanel",
		_create_style(
			StrontiumTokens.SURFACE_ELEVATED,
			StrontiumTokens.BORDER_STANDARD,
			1
		)
	)


static func _configure_line_edit(
	theme: Theme
) -> void:
	theme.set_font_size(
		"font_size",
		"LineEdit",
		StrontiumTokens.FONT_SIZE_BODY
	)

	theme.set_color(
		"font_color",
		"LineEdit",
		StrontiumTokens.TEXT_PRIMARY
	)

	theme.set_color(
		"font_uneditable_color",
		"LineEdit",
		StrontiumTokens.TEXT_MUTED
	)

	theme.set_color(
		"caret_color",
		"LineEdit",
		StrontiumTokens.ACCENT_PRIMARY
	)

	theme.set_color(
		"selection_color",
		"LineEdit",
		Color(
			StrontiumTokens.ACCENT_PRIMARY,
			0.25
		)
	)

	theme.set_stylebox(
		"normal",
		"LineEdit",
		_create_input_style(
			StrontiumTokens.SURFACE_PRIMARY,
			StrontiumTokens.BORDER_SUBTLE
		)
	)

	theme.set_stylebox(
		"focus",
		"LineEdit",
		_create_input_style(
			StrontiumTokens.SURFACE_ELEVATED,
			StrontiumTokens.ACCENT_PRIMARY
		)
	)

	theme.set_stylebox(
		"read_only",
		"LineEdit",
		_create_input_style(
			StrontiumTokens.BACKGROUND_TERTIARY,
			StrontiumTokens.BORDER_SUBTLE
		)
	)


static func _configure_tabs(
	theme: Theme
) -> void:
	theme.set_font_size(
		"font_size",
		"TabBar",
		StrontiumTokens.FONT_SIZE_BODY
	)

	theme.set_color(
		"font_selected_color",
		"TabBar",
		StrontiumTokens.TEXT_PRIMARY
	)

	theme.set_color(
		"font_unselected_color",
		"TabBar",
		StrontiumTokens.TEXT_SECONDARY
	)

	theme.set_color(
		"font_hovered_color",
		"TabBar",
		StrontiumTokens.ACCENT_PRIMARY
	)

	theme.set_color(
		"font_disabled_color",
		"TabBar",
		StrontiumTokens.INTERACTION_DISABLED
	)


static func _configure_sliders(
	theme: Theme
) -> void:
	theme.set_color(
		"font_color",
		"HSlider",
		StrontiumTokens.TEXT_SECONDARY
	)

	theme.set_stylebox(
		"slider",
		"HSlider",
		_create_slider_style(
			StrontiumTokens.BORDER_STANDARD
		)
	)

	theme.set_stylebox(
		"grabber_area",
		"HSlider",
		_create_slider_fill_style()
	)

	theme.set_stylebox(
		"grabber_area_highlight",
		"HSlider",
		_create_slider_fill_style()
	)

	theme.set_stylebox(
		"slider",
		"VSlider",
		_create_slider_style(
			StrontiumTokens.BORDER_STANDARD
		)
	)

	theme.set_stylebox(
		"grabber_area",
		"VSlider",
		_create_slider_fill_style()
	)

	theme.set_stylebox(
		"grabber_area_highlight",
		"VSlider",
		_create_slider_fill_style()
	)


static func _configure_progress_bars(
	theme: Theme
) -> void:
	theme.set_stylebox(
		"background",
		"ProgressBar",
		_create_style(
			StrontiumTokens.BACKGROUND_TERTIARY,
			StrontiumTokens.BORDER_SUBTLE,
			1
		)
	)

	theme.set_stylebox(
		"fill",
		"ProgressBar",
		_create_fill_style()
	)


static func _configure_popups(
	theme: Theme
) -> void:
	theme.set_stylebox(
		"panel",
		"PopupMenu",
		_create_style(
			StrontiumTokens.SURFACE_ELEVATED,
			StrontiumTokens.BORDER_STANDARD,
			1
		)
	)

	theme.set_color(
		"font_color",
		"PopupMenu",
		StrontiumTokens.TEXT_SECONDARY
	)

	theme.set_color(
		"font_hover_color",
		"PopupMenu",
		StrontiumTokens.TEXT_PRIMARY
	)

	theme.set_color(
		"font_accelerator_color",
		"PopupMenu",
		StrontiumTokens.TEXT_MUTED
	)

	theme.set_color(
		"font_disabled_color",
		"PopupMenu",
		StrontiumTokens.INTERACTION_DISABLED
	)


static func _configure_menu_buttons(
	theme: Theme
) -> void:
	theme.set_font_size(
		"font_size",
		"MenuButton",
		StrontiumTokens.FONT_SIZE_BODY
	)

	theme.set_color(
		"font_color",
		"MenuButton",
		StrontiumTokens.TEXT_SECONDARY
	)

	theme.set_color(
		"font_hover_color",
		"MenuButton",
		StrontiumTokens.ACCENT_PRIMARY
	)

	theme.set_color(
		"font_pressed_color",
		"MenuButton",
		StrontiumTokens.TEXT_PRIMARY
	)

	theme.set_color(
		"font_disabled_color",
		"MenuButton",
		StrontiumTokens.INTERACTION_DISABLED
	)


static func _create_style(
	background: Color,
	border: Color,
	border_width: int
) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()

	style.bg_color = background
	style.border_color = border

	style.set_border_width(
		SIDE_LEFT,
		border_width
	)

	style.set_border_width(
		SIDE_TOP,
		border_width
	)

	style.set_border_width(
		SIDE_RIGHT,
		border_width
	)

	style.set_border_width(
		SIDE_BOTTOM,
		border_width
	)

	style.corner_radius_top_left = (
		StrontiumTokens.RADIUS_SMALL
	)

	style.corner_radius_top_right = (
		StrontiumTokens.RADIUS_SMALL
	)

	style.corner_radius_bottom_left = (
		StrontiumTokens.RADIUS_SMALL
	)

	style.corner_radius_bottom_right = (
		StrontiumTokens.RADIUS_SMALL
	)

	style.content_margin_left = (
		StrontiumTokens.SPACE_LG
	)

	style.content_margin_right = (
		StrontiumTokens.SPACE_LG
	)

	style.content_margin_top = (
		StrontiumTokens.SPACE_SM
	)

	style.content_margin_bottom = (
		StrontiumTokens.SPACE_SM
	)

	return style


static func _create_input_style(
	background: Color,
	border: Color
) -> StyleBoxFlat:
	var style := _create_style(
		background,
		border,
		StrontiumTokens.BORDER_WIDTH_STANDARD
	)

	style.corner_radius_top_left = (
		StrontiumTokens.RADIUS_STANDARD
	)

	style.corner_radius_top_right = (
		StrontiumTokens.RADIUS_STANDARD
	)

	style.corner_radius_bottom_left = (
		StrontiumTokens.RADIUS_STANDARD
	)

	style.corner_radius_bottom_right = (
		StrontiumTokens.RADIUS_STANDARD
	)

	style.content_margin_left = (
		StrontiumTokens.SPACE_MD
	)

	style.content_margin_right = (
		StrontiumTokens.SPACE_MD
	)

	return style


static func _create_slider_style(
	color: Color
) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()

	style.bg_color = color

	style.corner_radius_top_left = 3
	style.corner_radius_top_right = 3
	style.corner_radius_bottom_left = 3
	style.corner_radius_bottom_right = 3

	style.content_margin_top = 2
	style.content_margin_bottom = 2

	return style


static func _create_slider_fill_style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()

	style.bg_color = (
		StrontiumTokens.ACCENT_PRIMARY
	)

	style.corner_radius_top_left = 3
	style.corner_radius_top_right = 3
	style.corner_radius_bottom_left = 3
	style.corner_radius_bottom_right = 3

	return style


static func _create_fill_style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()

	style.bg_color = (
		StrontiumTokens.ACCENT_PRIMARY
	)

	style.corner_radius_top_left = (
		StrontiumTokens.RADIUS_SMALL
	)

	style.corner_radius_top_right = (
		StrontiumTokens.RADIUS_SMALL
	)

	style.corner_radius_bottom_left = (
		StrontiumTokens.RADIUS_SMALL
	)

	style.corner_radius_bottom_right = (
		StrontiumTokens.RADIUS_SMALL
	)

	style.shadow_color = Color(
		StrontiumTokens.ACCENT_PRIMARY,
		0.25
	)

	style.shadow_size = 5

	return style
