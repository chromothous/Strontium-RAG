class_name StrontiumChat
extends Control


signal query_submitted(query: String)
signal message_added(message: Dictionary)
signal conversation_cleared()
signal source_selected(source: Dictionary)
signal citation_expanded(citation: Dictionary)


const CONTENT_MARGIN: int = 32
const PANEL_PADDING: int = 24

const ROLE_USER: String = "user"
const ROLE_ASSISTANT: String = "assistant"
const ROLE_SYSTEM: String = "system"

const STATE_READY: String = "READY"
const STATE_LOADING: String = "LOADING"
const STATE_WAITING_BACKEND: String = "WAITING FOR BACKEND"
const STATE_ERROR: String = "ERROR"


var state: String = STATE_READY
var messages: Array[Dictionary] = []

var conversation_scroll: ScrollContainer = null
var message_container: VBoxContainer = null
var input_field: TextEdit = null
var send_button: Button = null
var state_label: Label = null


func _ready() -> void:
	set_anchors_and_offsets_preset(
		Control.PRESET_FULL_RECT
	)

	mouse_filter = Control.MOUSE_FILTER_PASS

	_build_interface()
	_set_state(
		STATE_READY
	)


func _build_interface() -> void:
	for child in get_children():
		child.queue_free()

	var margin: MarginContainer = MarginContainer.new()

	margin.set_anchors_and_offsets_preset(
		Control.PRESET_FULL_RECT
	)

	margin.add_theme_constant_override(
		"margin_left",
		CONTENT_MARGIN
	)

	margin.add_theme_constant_override(
		"margin_top",
		CONTENT_MARGIN
	)

	margin.add_theme_constant_override(
		"margin_right",
		CONTENT_MARGIN
	)

	margin.add_theme_constant_override(
		"margin_bottom",
		CONTENT_MARGIN
	)

	add_child(
		margin
	)

	var content: VBoxContainer = VBoxContainer.new()

	content.add_theme_constant_override(
		"separation",
		16
	)

	margin.add_child(
		content
	)

	_build_header(
		content
	)

	_build_conversation(
		content
	)

	_build_composer(
		content
	)


func _build_header(
	parent: VBoxContainer
) -> void:
	var header: HBoxContainer = HBoxContainer.new()

	header.custom_minimum_size = Vector2(
		0.0,
		60.0
	)

	parent.add_child(
		header
	)

	var title_box: VBoxContainer = VBoxContainer.new()

	title_box.size_flags_horizontal = (
		Control.SIZE_EXPAND_FILL
	)

	title_box.add_theme_constant_override(
		"separation",
		2
	)

	header.add_child(
		title_box
	)

	var title: Label = Label.new()

	title.text = "CHAT"

	title.add_theme_font_size_override(
		"font_size",
		30
	)

	title.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_PRIMARY
	)

	title_box.add_child(
		title
	)

	var subtitle: Label = Label.new()

	subtitle.text = (
		"Ask questions about the Strontium knowledge base."
	)

	subtitle.add_theme_font_size_override(
		"font_size",
		14
	)

	subtitle.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	title_box.add_child(
		subtitle
	)

	state_label = Label.new()

	state_label.text = STATE_READY

	state_label.horizontal_alignment = (
		HORIZONTAL_ALIGNMENT_RIGHT
	)

	state_label.vertical_alignment = (
		VERTICAL_ALIGNMENT_CENTER
	)

	state_label.custom_minimum_size = Vector2(
		210.0,
		40.0
	)

	state_label.add_theme_font_size_override(
		"font_size",
		12
	)

	state_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	header.add_child(
		state_label
	)


func _build_conversation(
	parent: VBoxContainer
) -> void:
	var panel: PanelContainer = _create_panel()

	panel.size_flags_vertical = (
		Control.SIZE_EXPAND_FILL
	)

	parent.add_child(
		panel
	)

	var margin: MarginContainer = _create_panel_margin(
		panel
	)

	conversation_scroll = ScrollContainer.new()

	conversation_scroll.horizontal_scroll_mode = (
		ScrollContainer.SCROLL_MODE_DISABLED
	)

	conversation_scroll.vertical_scroll_mode = (
		ScrollContainer.SCROLL_MODE_AUTO
	)

	conversation_scroll.size_flags_vertical = (
		Control.SIZE_EXPAND_FILL
	)

	margin.add_child(
		conversation_scroll
	)

	message_container = VBoxContainer.new()

	message_container.size_flags_horizontal = (
		Control.SIZE_EXPAND_FILL
	)

	message_container.add_theme_constant_override(
		"separation",
		12
	)

	conversation_scroll.add_child(
		message_container
	)

	_show_empty_state()


func _build_composer(
	parent: VBoxContainer
) -> void:
	var panel: PanelContainer = _create_panel()

	panel.custom_minimum_size = Vector2(
		0.0,
		165.0
	)

	parent.add_child(
		panel
	)

	var margin: MarginContainer = _create_panel_margin(
		panel
	)

	var content: VBoxContainer = VBoxContainer.new()

	content.add_theme_constant_override(
		"separation",
		10
	)

	margin.add_child(
		content
	)

	var row: HBoxContainer = HBoxContainer.new()

	row.add_theme_constant_override(
		"separation",
		12
	)

	content.add_child(
		row
	)

	input_field = TextEdit.new()

	input_field.placeholder_text = (
		"Ask a question about your documents..."
	)

	input_field.custom_minimum_size = Vector2(
		0.0,
		90.0
	)

	input_field.size_flags_horizontal = (
		Control.SIZE_EXPAND_FILL
	)

	input_field.wrap_mode = (
		TextEdit.LINE_WRAPPING_BOUNDARY
	)

	input_field.text_changed.connect(
		_on_input_changed
	)

	input_field.gui_input.connect(
		_on_input_gui_input
	)

	row.add_child(
		input_field
	)

	var actions: VBoxContainer = VBoxContainer.new()

	actions.custom_minimum_size = Vector2(
		125.0,
		0.0
	)

	actions.add_theme_constant_override(
		"separation",
		8
	)

	row.add_child(
		actions
	)

	send_button = Button.new()

	send_button.text = "SEND"

	send_button.custom_minimum_size = Vector2(
		0.0,
		44.0
	)

	send_button.pressed.connect(
		_submit_query
	)

	actions.add_child(
		send_button
	)

	var clear_button: Button = Button.new()

	clear_button.text = "CLEAR CHAT"

	clear_button.custom_minimum_size = Vector2(
		0.0,
		44.0
	)

	clear_button.pressed.connect(
		_clear_conversation
	)

	actions.add_child(
		clear_button
	)

	var hint: Label = Label.new()

	hint.text = "Queries are emitted to the application integration layer. No backend answer is fabricated here."

	hint.add_theme_font_size_override(
		"font_size",
		12
	)

	hint.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	hint.autowrap_mode = (
		TextServer.AUTOWRAP_WORD_SMART
	)

	content.add_child(
		hint
	)


func _on_input_changed() -> void:
	_update_send_state()


func _on_input_gui_input(
	event: InputEvent
) -> void:
	if not event is InputEventKey:
		return

	var key_event: InputEventKey = event

	if not key_event.pressed:
		return

	if key_event.keycode != KEY_ENTER:
		return

	if key_event.shift_pressed:
		return

	if key_event.ctrl_pressed:
		return

	if key_event.alt_pressed:
		return

	if key_event.meta_pressed:
		return

	get_viewport().set_input_as_handled()

	_submit_query()


func _update_send_state() -> void:
	if send_button == null:
		return

	if input_field == null:
		return

	var can_send: bool = (
		not input_field.text.strip_edges().is_empty()
	)

	if state == STATE_LOADING:
		can_send = false

	send_button.disabled = not can_send


func _submit_query() -> void:
	if input_field == null:
		return

	var query: String = (
		input_field.text.strip_edges()
	)

	if query.is_empty():
		return

	add_user_message(
		query
	)

	input_field.text = ""

	_set_state(
		STATE_WAITING_BACKEND
	)

	query_submitted.emit(
		query
	)


func add_user_message(
	content: String
) -> void:
	_add_message(
		{
			"role": ROLE_USER,
			"content": content,
			"sources": []
		}
	)


func add_assistant_message(
	content: String,
	sources: Array = []
) -> void:
	_add_message(
		{
			"role": ROLE_ASSISTANT,
			"content": content,
			"sources": sources.duplicate(
				true
			)
		}
	)


func add_system_message(
	content: String
) -> void:
	_add_message(
		{
			"role": ROLE_SYSTEM,
			"content": content,
			"sources": []
		}
	)


func _add_message(
	message: Dictionary
) -> void:
	messages.append(
		message.duplicate(
			true
		)
	)

	for child in message_container.get_children():
		if child.name == "EmptyState":
			child.queue_free()

	var card: PanelContainer = _create_message_card(
		message
	)

	message_container.add_child(
		card
	)

	message_added.emit(
		message.duplicate(
			true
		)
	)

	call_deferred(
		"_scroll_to_bottom"
	)


func _create_message_card(
	message: Dictionary
) -> PanelContainer:
	var role: String = str(
		message.get(
			"role",
			ROLE_SYSTEM
		)
	)

	var card: PanelContainer = _create_panel()

	var margin: MarginContainer = _create_panel_margin(
		card
	)

	var content: VBoxContainer = VBoxContainer.new()

	content.add_theme_constant_override(
		"separation",
		8
	)

	margin.add_child(
		content
	)

	var header: HBoxContainer = HBoxContainer.new()

	content.add_child(
		header
	)

	var role_label: Label = Label.new()

	role_label.text = _role_display_name(
		role
	)

	role_label.size_flags_horizontal = (
		Control.SIZE_EXPAND_FILL
	)

	role_label.add_theme_font_size_override(
		"font_size",
		12
	)

	role_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_PRIMARY
	)

	header.add_child(
		role_label
	)

	var type_label: Label = Label.new()

	type_label.text = _role_type_name(
		role
	)

	type_label.add_theme_font_size_override(
		"font_size",
		10
	)

	type_label.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	header.add_child(
		type_label
	)

	var body: Label = Label.new()

	body.text = str(
		message.get(
			"content",
			""
		)
	)

	body.add_theme_font_size_override(
		"font_size",
		15
	)

	body.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_PRIMARY
	)

	body.autowrap_mode = (
		TextServer.AUTOWRAP_WORD_SMART
	)

	content.add_child(
		body
	)

	var sources: Variant = message.get(
		"sources",
		[]
	)

	if role == ROLE_ASSISTANT:
		if sources is Array:
			if not sources.is_empty():
				_add_citations(
					content,
					sources
				)

	return card


func _add_citations(
	parent: VBoxContainer,
	sources: Array
) -> void:
	var heading: Label = Label.new()

	heading.text = "CITATIONS"

	heading.add_theme_font_size_override(
		"font_size",
		11
	)

	heading.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	parent.add_child(
		heading
	)

	var citations: VBoxContainer = VBoxContainer.new()

	citations.add_theme_constant_override(
		"separation",
		6
	)

	parent.add_child(
		citations
	)

	for source_value in sources:
		var citation_data: Dictionary = {}

		if source_value is Dictionary:
			citation_data = source_value.duplicate(
				true
			)
		else:
			citation_data = {
				"citation_id": "CITATION",
				"title": str(
					source_value
				),
				"source": str(
					source_value
				)
			}

		var citation: StrontiumCitation = (
			StrontiumCitation.new()
		)

		citation.setup(
			citation_data
		)

		citation.custom_minimum_size = Vector2(
			0.0,
			60.0
		)

		citation.expanded.connect(
			_on_citation_expanded
		)

		citation.source_pressed.connect(
			_on_source_pressed
		)

		citations.add_child(
			citation
		)


func _on_citation_expanded(
	citation: Dictionary
) -> void:
	citation_expanded.emit(
		citation.duplicate(
			true
		)
	)


func _on_source_pressed(
	source: Dictionary
) -> void:
	source_selected.emit(
		source.duplicate(
			true
		)
	)


func set_loading() -> void:
	_set_state(
		STATE_LOADING
	)


func set_waiting_for_backend(
	detail: String = ""
) -> void:
	_set_state(
		STATE_WAITING_BACKEND,
		detail
	)


func set_response(
	content: String,
	sources: Array = []
) -> void:
	add_assistant_message(
		content,
		sources
	)

	_set_state(
		STATE_READY
	)


func set_error(
	detail: String
) -> void:
	add_system_message(
		detail
	)

	_set_state(
		STATE_ERROR,
		detail
	)


func _clear_conversation() -> void:
	messages.clear()

	for child in message_container.get_children():
		child.queue_free()

	_show_empty_state()

	_set_state(
		STATE_READY
	)

	conversation_cleared.emit()


func _show_empty_state() -> void:
	var empty: Label = Label.new()

	empty.name = "EmptyState"

	empty.text = (
		"Start a conversation by asking a question."
	)

	empty.horizontal_alignment = (
		HORIZONTAL_ALIGNMENT_CENTER
	)

	empty.vertical_alignment = (
		VERTICAL_ALIGNMENT_CENTER
	)

	empty.custom_minimum_size = Vector2(
		0.0,
		180.0
	)

	empty.add_theme_font_size_override(
		"font_size",
		16
	)

	empty.add_theme_color_override(
		"font_color",
		StrontiumTokens.TEXT_SECONDARY
	)

	message_container.add_child(
		empty
	)


func _scroll_to_bottom() -> void:
	if conversation_scroll == null:
		return

	var scrollbar: VScrollBar = (
		conversation_scroll.get_v_scroll_bar()
	)

	if scrollbar == null:
		return

	conversation_scroll.scroll_vertical = (
		int(scrollbar.max_value)
	)


func _set_state(
	new_state: String,
	detail: String = ""
) -> void:
	state = new_state

	if state_label != null:
		if detail.is_empty():
			state_label.text = new_state
		else:
			state_label.text = detail

	_update_send_state()


func _role_display_name(
	role: String
) -> String:
	match role:
		ROLE_USER:
			return "YOU"

		ROLE_ASSISTANT:
			return "STRONTIUM"

		ROLE_SYSTEM:
			return "SYSTEM"

	return role.to_upper()


func _role_type_name(
	role: String
) -> String:
	match role:
		ROLE_USER:
			return "QUERY"

		ROLE_ASSISTANT:
			return "RESPONSE"

		ROLE_SYSTEM:
			return "SYSTEM"

	return "MESSAGE"


func get_messages() -> Array[Dictionary]:
	return messages.duplicate(
		true
	)


func get_state() -> String:
	return state


func get_current_query() -> String:
	if input_field == null:
		return ""

	return input_field.text


func _create_panel() -> PanelContainer:
	var panel: PanelContainer = PanelContainer.new()

	var style: StyleBoxFlat = StyleBoxFlat.new()

	style.bg_color = Color(
		0.045,
		0.055,
		0.085,
		0.96
	)

	style.border_width_left = 1
	style.border_width_top = 1
	style.border_width_right = 1
	style.border_width_bottom = 1

	style.border_color = Color(
		0.15,
		0.18,
		0.24,
		0.90
	)

	style.corner_radius_top_left = 8
	style.corner_radius_top_right = 8
	style.corner_radius_bottom_left = 8
	style.corner_radius_bottom_right = 8

	panel.add_theme_stylebox_override(
		"panel",
		style
	)

	return panel


func _create_panel_margin(
	panel: PanelContainer
) -> MarginContainer:
	var margin: MarginContainer = MarginContainer.new()

	margin.add_theme_constant_override(
		"margin_left",
		PANEL_PADDING
	)

	margin.add_theme_constant_override(
		"margin_top",
		PANEL_PADDING
	)

	margin.add_theme_constant_override(
		"margin_right",
		PANEL_PADDING
	)

	margin.add_theme_constant_override(
		"margin_bottom",
		PANEL_PADDING
	)

	panel.add_child(
		margin
	)

	return margin
