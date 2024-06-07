import logging

from pymodbus.client.sync import ModbusTcpClient
from pymodbus.exceptions import ConnectionException, ModbusIOException


class UsrW610:
    _instance = None

    def __new__(
        cls,
        connection_type="TCP",
        ip_address=None,
        port=None,
        serial_port=None,
        baudrate=9600,
    ):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(
                connection_type, ip_address, port, serial_port, baudrate
            )
        return cls._instance

    def _initialize(self, connection_type, ip_address, port, serial_port, baudrate):
        self.logger = logging.getLogger("UsrW610")
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.connection_type = connection_type
        if connection_type == "TCP":
            self.client = ModbusTcpClient(ip_address, port=port)
        else:
            self.logger.error(f"Unsupported connection type: {connection_type}")
            raise ValueError("Unsupported connection type")

    def update_ip_and_port(self, new_ip_address, new_port):
        if self.connection_type != "TCP":
            self.logger.error("Cannot update IP and Port for non-TCP connection")
            return
        else:
            self.client = ModbusTcpClient(
                host=new_ip_address, port=new_port, auto_open=True, auto_close=True
            )

    def connect(self):
        try:
            if self.client.connect():
                self.logger.info("Connection successful")
                return True
            else:
                self.logger.error("Failed to connect")
                return False
        except ConnectionException as e:
            self.logger.error(f"Connection failed: {e}")
            return False

    def close_connection(self):
        self.client.close()
        self.logger.info("Connection closed")

    def read_input_register(self, start_reg, length=2, unit=1):
        try:
            regs = self.client.read_input_registers(start_reg, length, unit=unit)
            if not regs.isError():
                return regs.registers
            else:
                self.logger.error(f"Failed to read input registers: {regs}")
                return None
        except ModbusIOException as e:
            self.logger.error(f"Modbus IO Error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to read input registers: {e}")
            return None
