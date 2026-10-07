class BackendArchitecture:
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

    BOUNDARIES = (
        "api",
        "python_application",
        "container",
        "filesystem",
        "network",
        "authentication",
        "secret",
        "process",
        "configuration",
    )

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
    def get_boundaries(cls):
        return tuple(cls.BOUNDARIES)

    @classmethod
    def has_boundary(cls, boundary):
        if not isinstance(boundary, str):
            raise TypeError("Boundary must be a string.")
        return boundary.strip().lower() in cls.BOUNDARIES

    @classmethod
    def get_definition(cls):
        return {
            "authorities": {
                component: tuple(responsibilities)
                for component, responsibilities in cls.AUTHORITIES.items()
            },
            "boundaries": tuple(cls.BOUNDARIES),
        }

    @classmethod
    def is_defined(cls):
        required_components = {
            "godot",
            "api",
            "python",
            "docker",
        }
        required_boundaries = {
            "api",
            "python_application",
            "container",
            "filesystem",
            "network",
            "authentication",
            "secret",
            "process",
            "configuration",
        }
        return (
            set(cls.AUTHORITIES.keys()) == required_components
            and set(cls.BOUNDARIES) == required_boundaries
            and all(
                isinstance(responsibilities, tuple) and responsibilities
                for responsibilities in cls.AUTHORITIES.values()
            )
        )