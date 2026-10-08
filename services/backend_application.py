from configuration.backend_architecture import BackendArchitecture


class BackendApplication:
    def __init__(self):
        self.architecture = BackendArchitecture
        self.initialized = False

    def initialize(self):
        if not self.architecture.is_defined():
            raise RuntimeError("Backend architecture is not defined.")
        self.initialized = True

    def is_initialized(self):
        return self.initialized

    def get_architecture(self):
        return self.architecture.get_definition()