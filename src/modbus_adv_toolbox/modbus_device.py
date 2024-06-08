import time

from modbus_adv_toolbox.utils.logger import Logger


class ModbusDevice:
    _instance = None

    def __new__(cls, ip_address, port):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(ip_address, port)
        return cls._instance

    def _initialize(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        self.logger = Logger(name=self.__class__.__name__)._set_logger()
        self.client = self._create_client(ip_address, port)
        self._test_connection()

    def _create_client(self, ip_address, port):
        raise NotImplementedError("Subclasses must implement this method")

    def _test_connection(self, max_attempts=3):
        """
        Test the connection to the device.

        Args:
            max_attempts (int): Maximum number of connection attempts.

        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        for attempt in range(1, max_attempts + 1):
            try:
                self.client.open()
                self.logger.info(f"Successful connection attempt {attempt}")
                return True
            except Exception as e:
                self.logger.error(f"Failed connection attempt {attempt}: {e}")
                if attempt < max_attempts:
                    self.logger.info("Retrying...")
                    time.sleep(1)
        self.logger.error("Failed to establish connection after multiple attempts")
        return False
