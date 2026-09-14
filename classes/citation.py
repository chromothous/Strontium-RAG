from classes.logger import Logger


class Citation:
    def __init__(self, logger):
        if not isinstance(logger, Logger):
            raise ValueError("Citation logger must be a Logger")
        self.logger = logger

    def cite(self, answer, sources):
        self.logger.info("Citation request received")
        return None