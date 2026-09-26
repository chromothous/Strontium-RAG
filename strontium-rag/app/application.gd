extends Node

signal startup_completed
signal shutdown_started


@onready var app_state: Node = ApplicationState
@onready var application_window: Window = get_window()
@onready var application_service: Node = $ApplicationService
@onready var navigation_service: Node = $NavigationService
@onready var screen_registry: ScreenRegistry = $ScreenRegistry
@onready var debug_service: DebugService = $DebugService
@onready var content_root: Control = $UIRoot/ContentRoot


func _ready() -> void:
	application_window.close_requested.connect(_on_close_requested)
	start_application()


func start_application() -> void:
	app_state.mark_starting()

	print("Strontium RAG application starting.")

	debug_service.initialize()
	debug_service.write("Application startup sequence beginning.")

	application_service.initialize()
	debug_service.write("ApplicationService initialized.")

	screen_registry.initialize()
	debug_service.write("ScreenRegistry initialized.")

	navigation_service.configure(content_root, screen_registry)
	debug_service.write("NavigationService configured.")

	navigation_service.navigate_to("Home")
	debug_service.write("Initial navigation completed.")

	app_state.mark_ready()
	startup_completed.emit()

	print("Strontium RAG application initialized.")
	print("Application state: " + app_state.get_status_name())
	print("Application service initialized: " + str(application_service.is_initialized()))
	print("Registered destinations: " + str(screen_registry.get_destinations()))
	print("Current destination: " + navigation_service.get_current_destination())


func shutdown_application() -> void:
	if app_state.is_shutting_down():
		return

	app_state.begin_shutdown()
	shutdown_started.emit()

	debug_service.write("Application shutdown sequence beginning.")

	application_service.shutdown()
	debug_service.write("ApplicationService shutdown completed.")

	debug_service.shutdown()

	print("Strontium RAG application shutting down.")
	print("Application service shutting down: " + str(application_service.is_shutting_down()))


func _on_close_requested() -> void:
	shutdown_application()
	get_tree().quit()


func _exit_tree() -> void:
	if not app_state.is_shutting_down():
		shutdown_application()
