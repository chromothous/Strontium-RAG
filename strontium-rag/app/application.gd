extends Node


signal startup_completed
signal shutdown_started


@onready var app_state: Node = ApplicationState
@onready var application_window: Window = get_window()
@onready var application_service: Node = $ApplicationService
@onready var navigation_service: Node = $NavigationService
@onready var screen_registry: ScreenRegistry = $ScreenRegistry
@onready var debug_service: DebugService = $DebugService
@onready var ui_root: Control = $UIRoot
@onready var content_root: Control = $UIRoot/ContentRoot
@onready var modal_root: Control = $UIRoot/ModalRoot
@onready var header: StrontiumHeader = (
	$UIRoot/HeaderRoot as StrontiumHeader
)
@onready var navigation_ui: StrontiumNavigation = (
	$UIRoot/NavigationRoot as StrontiumNavigation
)
@onready var footer: StrontiumFooter = (
	$UIRoot/StatusRoot as StrontiumFooter
)


var theme_service: StrontiumThemeService


func _ready() -> void:
	application_window.close_requested.connect(
		_on_close_requested
	)

	modal_root.mouse_filter = Control.MOUSE_FILTER_IGNORE

	_initialize_theme_service()

	navigation_service.navigation_changed.connect(
		_on_navigation_changed
	)

	header.set_status(
		"INITIALIZING",
		StrontiumTokens.STATE_INFO
	)

	footer.set_status(
		"STARTING",
		StrontiumStatusIndicator.StatusType.ACTIVE
	)

	start_application()


func _initialize_theme_service() -> void:
	theme_service = StrontiumThemeService.new()
	theme_service.name = "ThemeService"

	add_child(theme_service)

	theme_service.configure(
		ui_root
	)

	theme_service.initialize()

	debug_service.write(
        "Global Strontium theme applied."
	)


func start_application() -> void:
	app_state.mark_starting()

	header.set_status(
		"STARTING",
		StrontiumTokens.STATE_INFO
	)

	footer.set_status(
		"STARTING",
		StrontiumStatusIndicator.StatusType.ACTIVE
	)

	print(
        "Strontium RAG application starting."
	)

	debug_service.initialize()

	debug_service.write(
        "Application startup sequence beginning."
	)

	application_service.initialize()

	debug_service.write(
        "ApplicationService initialized."
	)

	screen_registry.initialize()

	debug_service.write(
        "ScreenRegistry initialized."
	)

	navigation_service.configure(
		content_root,
		screen_registry
	)

	debug_service.write(
        "NavigationService configured."
	)

	navigation_ui.configure(
		navigation_service,
		screen_registry
	)

	debug_service.write(
        "Navigation UI configured."
	)

	navigation_service.navigate_to(
        "Home"
	)

	debug_service.write(
        "Initial navigation completed."
	)

	footer.set_destination(
		navigation_service.get_current_destination()
	)

	app_state.mark_ready()

	header.set_status(
		"SYSTEM READY",
		StrontiumTokens.STATE_SUCCESS
	)

	footer.set_status(
		"READY",
		StrontiumStatusIndicator.StatusType.SUCCESS
	)

	startup_completed.emit()

	print(
        "Strontium RAG application initialized."
	)

	print(
        "Application state: "
		+ app_state.get_status_name()
	)

	print(
        "Application service initialized: "
		+ str(
			application_service.is_initialized()
		)
	)

	print(
        "Registered destinations: "
		+ str(
			screen_registry.get_destinations()
		)
	)

	print(
        "Current destination: "
		+ navigation_service.get_current_destination()
	)


func shutdown_application() -> void:
	if app_state.is_shutting_down():
		return

	app_state.begin_shutdown()

	header.set_status(
		"SHUTTING DOWN",
		StrontiumTokens.STATE_WARNING
	)

	footer.set_status(
		"SHUTTING DOWN",
		StrontiumStatusIndicator.StatusType.WARNING
	)

	shutdown_started.emit()

	debug_service.write(
        "Application shutdown sequence beginning."
	)

	application_service.shutdown()

	debug_service.write(
        "ApplicationService shutdown completed."
	)

	debug_service.shutdown()

	print(
        "Strontium RAG application shutting down."
	)

	print(
        "Application service shutting down: "
		+ str(
			application_service.is_shutting_down()
		)
	)


func _on_navigation_changed(
	_previous_destination: String,
	current_destination: String
) -> void:
	footer.set_destination(
		current_destination
	)


func _on_close_requested() -> void:
	shutdown_application()
	get_tree().quit()


func _exit_tree() -> void:
	if not app_state.is_shutting_down():
		shutdown_application()
