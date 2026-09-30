class_name StrontiumCitation
extends PanelContainer


signal expanded(citation: Dictionary)
signal source_pressed(citation: Dictionary)


const PADDING: int = 14


var citation: Dictionary = {}
var expanded_state: bool = false

var citation_button: Button = null
var detail_container: VBoxContainer = null


func setup(
	new_citation: Dictionary
) -> void:
	citation = new_citation.duplicate(
		true
	)

	if is_inside_tree():
		_build_interface()


func _ready() -> void:
	_build_interface()


func _build_interface() -> void:
	for child in get_children():
		child.queue_free()

	var margin: MarginContainer = MarginContainer.new()

	margin.add_theme_constant_override(
		"margin_left",
		PADDING
	)

	margin.add_theme_constant_override(
		"margin_top",
		PADDING
	)

	margin.add_theme_constant_override(
		"margin_right",
		PADDING
	)

	margin.add_theme_constant_override(
		"margin_bottom",
		PADDING
	)

	add_child(
		margin
	)

	var content: VBoxContainer = VBoxContainer.new()

	content.add_theme_constant_override(
		"separation",
		8
	)

	margin.add_child(
		content
	)

	citation_button = Button.new()

	citation_button.alignment = (
		HORIZONTAL_ALIGNMENT_LEFT
	)

	citation_button.custom_minimum_size = Vector2(
		0.0,
		46.0
	)

	citation_button.text = _build_summary()

	citation_button.pressed.connect(
		_toggle_expanded
	)

	content.add_child(
		citation_button
	)

	detail_container = VBoxContainer.new()

	detail_container.visible = expanded_state

	detail_container.add_theme_constant_override(
		"separation",
		8
	)

	content.add_child(
		detail_container
	)

	_build_details()


func _build_summary() -> String:
	var citation_id: String = str(
		citation.get(
			"citation_id",
			"CITATION"
		)
	)

	var title: String = str(
		citation.get(
			"title",
			citation.get(
				"source",
				"Unknown source"
			)
		)
	)

	var source: String = str(
		citation.get(
			"source",
			"Unknown source"
		)
	)

	return (
		"%s  •  %s  •  %s"
		% [
			citation_id,
			title,
			source
		]
	)


func _build_details() -> void:
	if detail_container == null:
		return

	for child in detail_container.get_children():
		child.queue_free()

	var identity: Label = _create_detail(
		"Source identity: %s"
		% str(
			citation.get(
				"source",
				"—"
			)
		)
	)

	detail_container.add_child(
		identity
	)

	var document_id: Label = _create_detail(
		"Document: %s"
		% str(
			citation.get(
				"document_id",
				"—"
			)
		)
	)

	detail_container.add_child(
		document_id
	)

	var chunk_id: Label = _create_detail(
		"Chunk: %s"
		% str(
			citation.get(
				"chunk_id",
				"—"
			)
		)
	)

	detail_container.add_child(
		chunk_id
	)

	var page: Label = _create_detail(
		"Page: %s"
		% str(
			citation.get(
				"page",
				"—"
			)
		)
	)

	detail_container.add_child(
		page
	)

	var relationship: Label = _create_detail(
		"Citation relationship: %s → %s"
		% [
			str(
				citation.get(
					"citation_id",
					"—"
				)
			),
			str(
				citation.get(
					"document_id",
					"—"
				)
			)
		]
	)

	detail_container.add_child(
		relationship
	)

	var context_heading: Label = _create_heading(
		"RETRIEVED CONTEXT"
	)

	detail_container.add_child(
		context_heading
	)

	var context: Label = _create_detail(
		str(
			citation.get(
				"context",
				"No retrieved context supplied."
			)
		)
	)

	context.autowrap_mode = (
		TextServer.AUTOWRAP_WORD_SMART
	)

	detail_container.add_child(
		context
	)

	var reference: Label = _create_detail(
		"Document reference: %s"
		% str(
			citation.get(
				"document_reference",
				citation.get(
					"document_id",
					"—"
				)
			)
		)
	)

	detail_container.add_child(
		reference
	)

	var source_button: Button = Button.new()

	source_button.text = "OPEN SOURCE REFERENCE"

	source_button.custom_minimum_size = Vector2(
		0.0,
		40.0
	)

	source_button.pressed.connect(
		_on_source_pressed
	)

	detail_container.add_child(
		source_button
	)


func _create_heading(
	value: String
) -> Label:
	var label: Label = Label.new()

	label.text = value

	label.add_theme_font_size_override(
		"font_size",
		11
	)

	label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	return label


func _create_detail(
	value: String
) -> Label:
	var label: Label = Label.new()

	label.text = value

	label.add_theme_font_size_override(
		"font_size",
		13
	)

	label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	label.autowrap_mode = (
		TextServer.AUTOWRAP_WORD_SMART
	)

	return label


func _toggle_expanded() -> void:
	expanded_state = not expanded_state

	if detail_container != null:
		detail_container.visible = expanded_state

	if expanded_state:
		expanded.emit(
			citation.duplicate(
				true
			)
		)


func _on_source_pressed() -> void:
	source_pressed.emit(
		citation.duplicate(
			true
		)
	)


func get_citation() -> Dictionary:
	return citation.duplicate(
		true
	)


func set_expanded(
	value: bool
) -> void:
	expanded_state = value

	if detail_container != null:
		detail_container.visible = value
