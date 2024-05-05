import logging


class Logger:
    """
    A Logger class that sets up and returns a logging object.

    Attributes:
        name (str): The name of the logger.
        logger (Logger): The logger object.

    Methods:
        _set_logger(): Sets up and returns a logger object.
    """

    def __init__(self, name: str = "base-logger"):
        """
        Constructs all the necessary attributes for the Logger object.

        Args:
            name (str): The name of the logger. Defaults to "base-logger".
        """
        self.name = name
        self.logger = self._set_logger()

    def _set_logger(self):
        """
        Sets up and returns a logger object.

        Returns:
            Logger: A logger object with a stream handler and a specific format.
        """
        app_logger = logging.getLogger(self.name)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        app_logger.addHandler(handler)
        app_logger.setLevel(logging.INFO)
        return app_logger
