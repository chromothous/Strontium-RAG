from classes.logger import Logger


class StartupConfiguration:
    ENVIRONMENTS = (
        "development",
        "testing",
        "production",
    )

    def __init__(
        self,
        logger,
        environment="production",
        debug=False,
        development_server=False,
    ):
        if not isinstance(logger, Logger):
            raise ValueError("Startup configuration logger must be a Logger")
        self.logger = logger
        self.environment = environment
        self.debug = debug
        self.development_server = development_server
        self.validate()

    def _reject(self, message):
        self.logger.error(message)
        raise ValueError(message)

    def validate(self):
        if not isinstance(self.environment, str):
            self._reject("Startup environment must be a string.")
        self.environment = self.environment.strip().lower()
        if self.environment not in self.ENVIRONMENTS:
            self._reject("Startup environment is not supported.")
        if type(self.debug) is not bool:
            self._reject("Startup debug setting must be a boolean.")
        if type(self.development_server) is not bool:
            self._reject("Development server setting must be a boolean.")
        if self.environment == "production" and self.debug:
            self._reject("Debug mode is not allowed in production.")
        if self.environment == "production" and self.development_server:
            self._reject("Development server is not allowed in production.")
        self.logger.info("Startup configuration validated successfully.")
        return True

    def is_production(self):
        return self.environment == "production"

    def get_definition(self):
        return {
            "environment": self.environment,
            "debug": self.debug,
            "development_server": self.development_server,
        }