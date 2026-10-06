class BackendAuthority:
    VERSION = "0.15.17.0.2"

    AUTHORITIES = {
        "godot": (
            "presentation",
            "interaction",
            "ui_state",
            "visualization",
        ),
        "api": (
            "authentication",
            "request_acceptance",
            "request_rejection",
            "routing",
            "request_response_contract",
            "security_enforcement",
        ),
        "python": (
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
            "security_enforcement",
        ),
        "docker": (
            "runtime_isolation",
            "filesystem_restrictions",
            "process_isolation",
            "resource_restrictions",
            "network_restrictions",
        ),
    }

    @classmethod
    def get_authority(cls, component):
        if not isinstance(component, str):
            raise TypeError("Component must be a string.")
        component = component.strip().lower()
        if component not in cls.AUTHORITIES:
            raise ValueError(f"Unknown backend component: {component}")
        return cls.AUTHORITIES[component]

    @classmethod
    def has_authority(cls, component, responsibility):
        if not isinstance(responsibility, str):
            raise TypeError("Responsibility must be a string.")
        responsibility = responsibility.strip().lower()
        return responsibility in cls.get_authority(component)

    @classmethod
    def get_definition(cls):
        return {
            "version": cls.VERSION,
            "authorities": {
                component: tuple(responsibilities)
                for component, responsibilities in cls.AUTHORITIES.items()
            },
        }

    @classmethod
    def is_defined(cls):
        required_components = {
            "godot",
            "api",
            "python",
            "docker",
        }
        return (
            set(cls.AUTHORITIES.keys()) == required_components
            and all(
                isinstance(responsibilities, tuple) and responsibilities
                for responsibilities in cls.AUTHORITIES.values()
            )
        )