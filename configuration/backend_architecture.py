from classes.logger import Logger


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

    def __init__(self, logger):
        if not isinstance(logger, Logger):
            raise ValueError("Backend architecture logger must be a Logger")
        self.logger = logger
        self.logger.info("Backend architecture initialized.")

    def get_authority(self, component):
        if not isinstance(component, str):
            self.logger.error("Backend component must be a string.")
            raise TypeError("Component must be a string.")
        component = component.strip().lower()
        if component not in self.AUTHORITIES:
            self.logger.error(f"Unknown backend component: {component}")
            raise ValueError(f"Unknown backend component: {component}")
        return self.AUTHORITIES[component]

    def has_authority(self, component, responsibility):
        if not isinstance(responsibility, str):
            self.logger.error("Backend responsibility must be a string.")
            raise TypeError("Responsibility must be a string.")
        responsibility = responsibility.strip().lower()
        return responsibility in self.get_authority(component)

    def get_boundaries(self):
        return tuple(self.BOUNDARIES)

    def has_boundary(self, boundary):
        if not isinstance(boundary, str):
            self.logger.error("Backend boundary must be a string.")
            raise TypeError("Boundary must be a string.")
        return boundary.strip().lower() in self.BOUNDARIES

    def get_definition(self):
        return {
            "authorities": {
                component: tuple(responsibilities)
                for component, responsibilities in self.AUTHORITIES.items()
            },
            "boundaries": tuple(self.BOUNDARIES),
        }

    def is_defined(self):
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
            set(self.AUTHORITIES.keys()) == required_components
            and set(self.BOUNDARIES) == required_boundaries
            and all(
                isinstance(responsibilities, tuple) and responsibilities
                for responsibilities in self.AUTHORITIES.values()
            )
        )