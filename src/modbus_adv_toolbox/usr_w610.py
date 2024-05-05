import time

import numpy as np
from pymodbus import client as ModbusClient
from pymodbus.client import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.exceptions import ModbusIOException  # Import the exception
from pymodbus.exceptions import ConnectionException
from pymodbus.payload import BinaryPayloadBuilder

from utils.logger import Logger


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
        self.logger = Logger(name="UsrW610")._set_logger()
        self.connection_type = connection_type
        if connection_type == "TCP":
            self.client = ModbusClient.ModbusTcpClient(ip_address, port=port)
        elif connection_type == "Serial":
            self.client = ModbusClient.ModbusSerialClient(
                method="rtu",
                port=serial_port,
                baudrate=baudrate,
                bytesize=8,
                parity="N",
                stopbits=1,
            )
        else:
            self.logger.error(f"Unsupported connection type: {connection_type}")
            raise ValueError("Unsupported connection type")

    def update_ip_and_port(self, new_ip_address, new_port):
        # check if connection type is TCP
        if self.connection_type != "TCP":
            self.logger.error("Cannot update IP and Port for non-TCP connection")
            return
        else:
            self.ip_address = new_ip_address
            self.port = new_port
            self.client = ModbusTcpClient(
                host=new_ip_address, port=new_port, auto_open=True, auto_close=True
            )

    def _test_connection(self, max_attempts=3):
        """
        Test the connection to the Modbus Device.

        Args:
            max_attempts (int): Maximum number of connection attempts.

        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        for attempt in range(1, max_attempts + 1):
            try:
                if self.client.connect():
                    self.logger.info(f"Successful connection attempt {attempt}")
                    return True
                else:
                    raise Exception("Connection attempt failed")
            except Exception as e:
                self.logger.error(f"Failed connection attempt {attempt}: {e}")
                if attempt < max_attempts:
                    self.logger.info("Retrying...")
                    time.sleep(1)
        self.logger.error("Failed to establish connection after multiple attempts")
        return False

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
        """Close the Modbus TCP connection."""
        self.client.close()
        self.logger.info("Connection closed")

    def read_register_raw(self, start_reg, length=36):
        """
        Read raw registers.

        Args:
            start_reg (int): Start register address.
            length (int): Number of registers to read.

        Returns:
            list: List of register values.
        """
        try:
            regs_l = self.client.read_holding_registers(start_reg, length)
            return regs_l
        except ModbusIOException as e:  # Catch ModbusIOException
            self.logger.error(f"Modbus IO Error: {e}")
            return None
        except Exception as e:  # Catch other exceptions
            self.logger.error(f"Failed to read registers: {e}")
            return None

    def read_analog_inputs(self):
        """
        Read analog input registers.

        Returns:
            dict: Dictionary containing values of IN1 and IN2 from both possible register addresses.
        """
        result = {}
        try:
            # Reading IN1 from the first possible address
            in1_first = self.client.read_holding_registers(
                40000, 1
            )  # Adjusted address for IN1
            result["IN1_first"] = (
                in1_first.registers if in1_first.isError() == False else None
            )

            # Reading IN1 from the second possible address
            in1_second = self.client.read_holding_registers(
                40064, 1
            )  # Adjusted address for IN1
            result["IN1_second"] = (
                in1_second.registers if in1_second.isError() == False else None
            )

            # Reading IN2 from the first possible address
            in2_first = self.client.read_holding_registers(
                40001, 1
            )  # Adjusted address for IN2
            result["IN2_first"] = (
                in2_first.registers if in2_first.isError() == False else None
            )

            # Reading IN2 from the second possible address
            in2_second = self.client.read_holding_registers(
                40065, 1
            )  # Adjusted address for IN2
            result["IN2_second"] = (
                in2_second.registers if in2_second.isError() == False else None
            )

        except ModbusIOException as e:
            self.logger.error(f"Modbus IO Error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to read registers: {e}")
            return None

        return result

    def write_random_values(self, start_reg, end_reg):
        """
        Write random float values to consecutive registers in the PLC.

        Args:
            start_reg (int): Start register address to write to.
            end_reg (int): End register address (exclusive).
        """
        try:
            for i in range(start_reg, end_reg - 2, 2):
                builder = BinaryPayloadBuilder(
                    byteorder=Endian.Big, wordorder=Endian.Little
                )
                value = np.random.uniform(0, 100)
                builder.add_32bit_float(value)
                payload = builder.build()
                self.client.write_registers(i - 2, payload, skip_encode=True)
        except Exception as e:
            self.logger.error(f"Failed to write random values: {e}")
