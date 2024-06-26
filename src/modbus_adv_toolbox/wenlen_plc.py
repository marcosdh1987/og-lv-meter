import logging
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.exceptions import ConnectionException, ModbusIOException
from pymodbus.payload import BinaryPayloadDecoder, BinaryPayloadBuilder

class WenlenPLC:
    _instance = None

    def __new__(cls, connection_type="TCP", ip_address=None, port=None, retries=2):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(connection_type, ip_address, port, retries)
        return cls._instance

    def _initialize(self, connection_type, ip_address, port, retries):
        self.retries = retries
        self.logger = logging.getLogger("WenlenPLC")
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

    def read_coils(self, start_reg, count=32, unit=1):
        try:
            result = self.client.read_coils(start_reg - 1, count, unit=unit)
            if not result.isError():
                return result.bits
            else:
                self.logger.error(f"Failed to read coils: {result}")
                return None
        except ModbusIOException as e:
            self.logger.error(f"Modbus IO Error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to read coils: {e}")
            return None

    def read_holding_registers(self, start_reg, length=2, unit=1):
        try:
            regs = self.client.read_holding_registers(start_reg - 1, length, unit=unit)
            if not regs.isError():
                return regs.registers
            else:
                self.logger.error(f"Failed to read holding registers: {regs}")
                return None
        except ModbusIOException as e:
            self.logger.error(f"Modbus IO Error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to read holding registers: {e}")
            return None

    def decode_register_cdab(self, registers):
        decoder = BinaryPayloadDecoder.fromRegisters(
            registers, byteorder=Endian.Big, wordorder=Endian.Little
        )
        return decoder.decode_32bit_float()

    def read_register_with_retries(self, start_reg, length=2, unit=1):
        for attempt in range(self.retries):
            result = self.read_holding_registers(start_reg, length, unit)
            if result is not None:
                return result
            self.logger.warning(
                f"Attempt {attempt + 1} failed for register {start_reg}. Retrying..."
            )
        self.logger.error(
            f"Failed to read register {start_reg} after {self.retries} attempts."
        )
        return None

    def read_boolean_registers(self, start_reg=10001, count=32, unit=1):
        return self.read_coils(start_reg, count, unit)

    def read_float_registers(self, start_reg=40001, count=4, unit=1):
        floats = []
        for i in range(count):
            regs = self.read_register_with_retries(start_reg + 2 * i, length=2, unit=unit)
            self.logger.info(f"Read registers for float {i}: {regs}")
            if regs:
                value = self.decode_register_cdab(regs)
                floats.append(value)
                self.logger.info(f"Decoded float value {i}: {value}")
            else:
                floats.append(None)
                self.logger.warning(f"Failed to read or decode float value {i}")
        return floats

    def write_coils(self, start_reg, values, unit=1):
        try:
            result = self.client.write_coils(start_reg - 1, values, unit=unit)
            if result.isError():
                self.logger.error(f"Failed to write coils: {result}")
                return False
            return True
        except ModbusIOException as e:
            self.logger.error(f"Modbus IO Error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to write coils: {e}")
            return False

    def write_register(self, start_reg, value, unit=1):
        try:
            builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Little)
            builder.add_32bit_float(value)
            payload = builder.to_registers()
            self.logger.info(f"Writing float value {value} to registers starting at {start_reg}: {payload}")
            result = self.client.write_registers(start_reg - 1, payload, unit=unit)
            self.logger.info(f"Write result for registers starting at {start_reg}: {result}")
            if result.isError():
                self.logger.error(f"Failed to write register: {result}")
                return False
            return True
        except ModbusIOException as e:
            self.logger.error(f"Modbus IO Error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to write register: {e}")
            return False