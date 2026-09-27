extends BaseScreen


@onready var test_card: StrontiumCard = $HomeContainer/TestCard


func _on_initialize() -> void:
	test_card.elevated = true
	test_card.glow_enabled = true
	test_card.interactive = true

	print("Strontium RAG Home screen initialized.")
	print("Interactive test card enabled: " + str(test_card.interactive))


func _on_enter() -> void:
	print("Strontium RAG Home screen entered.")


func _on_exit() -> void:
	print("Strontium RAG Home screen exited.")
