import struct
import time
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusIOException  # Import the exception
from utils.logger import Logger
import numpy as np


class UsrW610:
    _instance = None

    def __new__(cls, ip_address, port):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(ip_address, port)
        return cls._instance

    def _initialize(self, ip_address, port):
        self.logger = Logger(name="UsrW610")._set_logger()
        self.ip_address = ip_address
        self.port = port
        self.client = ModbusTcpClient(host=ip_address, port=port, auto_open=True, auto_close=True)
        self._test_connection()

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
                self.client.connect()
                self.logger.info(f"Successful connection attempt {attempt}")
                return True
            except Exception as e:
                self.logger.error(f"Failed connection attempt {attempt}: {e}")
                if attempt < max_attempts:
                    self.logger.info("Retrying...")
                    time.sleep(1)
        self.logger.error("Failed to establish connection after multiple attempts")
        return False
    
    def close_connection(self):
        """Close the Modbus TCP connection."""
        if self.client.is_socket_open():
            self.client.close()

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


    def write_random_values(self, start_reg, end_reg):
        """
        Write random float values to consecutive registers in the PLC.
        
        Args:
            start_reg (int): Start register address to write to.
            end_reg (int): End register address (exclusive).
        """
        try:
            for i in range(start_reg, end_reg - 2, 2):
                builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Little)
                value = np.random.uniform(0, 100)
                builder.add_32bit_float(value)
                payload = builder.build()
                self.client.write_registers(i - 2, payload, skip_encode=True)
        except Exception as e:
            self.logger.error(f"Failed to write random values: {e}")