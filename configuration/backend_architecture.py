class BackendArchitecture:
    VERSION = "0.15.17.0"

    GODOT_RESPONSIBILITIES = (
        "presentation",
        "interaction",
        "ui_state",
        "visualization"
    )

    API_RESPONSIBILITIES = (
        "authentication",
        "request_acceptance",
        "request_rejection",
        "routing",
        "request_response_contract",
        "security_enforcement"
    )

    PYTHON_RESPONSIBILITIES = (
        "ingestion",
        "preprocessing",
        "chunking",
        "embeddings",
        "vector_storage",
        "retrieval",
        "context",
        "generation",
        "citations",
        "conversation",
        "evaluation",
        "security_enforcement"
    )

    DOCKER_RESPONSIBILITIES = (
        "runtime_isolation",
        "filesystem_restrictions",
        "process_isolation",
        "resource_restrictions",
        "network_restrictions"
    )

    BOUNDARIES = (
        "api",
        "python_application",
        "container",
        "filesystem",
        "network",
        "authentication",
        "secret",
        "process",
        "configuration"
    )

    @classmethod
    def get_definition(cls):
        return {
            "version": cls.VERSION,
            "godot": cls.GODOT_RESPONSIBILITIES,
            "api": cls.API_RESPONSIBILITIES,
            "python": cls.PYTHON_RESPONSIBILITIES,
            "docker": cls.DOCKER_RESPONSIBILITIES,
            "boundaries": cls.BOUNDARIES
        }

    @classmethod
    def is_defined(cls):
        return (
            bool(cls.VERSION)
            and bool(cls.GODOT_RESPONSIBILITIES)
            and bool(cls.API_RESPONSIBILITIES)
            and bool(cls.PYTHON_RESPONSIBILITIES)
            and bool(cls.DOCKER_RESPONSIBILITIES)
            and bool(cls.BOUNDARIES)
        )