import struct
import time

from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder
from pyModbusTCP.client import ModbusClient

from modbus_adv_toolbox.utils.logger import Logger


class GenericPLC:
    _instance = None

    def __new__(cls, ip_address, port):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(ip_address, port)
        return cls._instance

    def _initialize(self, ip_address, port):
        self.logger = Logger(name="GenericPLC")._set_logger()
        self.ip_address = ip_address
        self.port = port
        self.client = ModbusClient(
            host=ip_address, port=port, auto_open=True, auto_close=True
        )
        self._test_connection()

    def update_ip_and_port(self, new_ip_address, new_port):
        self.ip_address = new_ip_address
        self.port = new_port
        self.client = ModbusClient(
            host=new_ip_address, port=new_port, auto_open=True, auto_close=True
        )

    def _test_connection(self, max_attempts=3):
        """
        Test the connection to the PLC.

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

    def read_plc_register_raw(self, start_reg, length=36):
        """
        Read a list of registers from the PLC. by default, it reads 36 registers.

        Args:
            start_reg (int): Start register address.
            length (int): Number of registers to read.

        Returns:
            list: List of register values.
        """
        regs_l = self.client.read_holding_registers(start_reg, length)
        return regs_l

    def write_single_float(self, register, value):
        builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big)
        builder.add_32bit_float(value)
        regs_to_write = builder.to_registers()
        result = self.client.write_multiple_registers(register, regs_to_write)
        if result:
            self.logger.info(
                f"Valor {value} escrito en el PLC, registros {register} y {register + 1}"
            )
        else:
            self.logger.info(
                f"Error al escribir el valor {value} en el PLC, registros {register} y {register + 1}"
            )

    def write_plc_register(self, start_reg, values):
        builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Little)
        for value in values:
            builder.add_32bit_float(value)
        regs_to_write = builder.to_registers()[::-1]
        result = self.client.write_multiple_registers(start_reg, regs_to_write)
        if result:
            self.logger.info("Valores escritos en el PLC:", values)
        else:
            self.logger.info("Error al escribir valores en el PLC")

    def decimal_decode(self, regs_l):
        number = float(regs_l[0]) + float("0." + str(regs_l[1]))
        return number

    def regs2float(self, regs):
        return struct.unpack("<f", struct.pack("<HH", *regs))[0]

    def read_plc_register_fast(self, start_reg, length=72):
        regs_l = self.client.read_holding_registers(start_reg, length)
        data = []
        for i in range(0, length, 2):
            data.append(self.regs2float(regs_l[i : i + 2]))
        return data

    def read_plc_register(self, start_reg, length=72, max_attempts=3):
        data = []
        attempts = 0
        while attempts < max_attempts:
            try:
                regs_l = self.client.read_holding_registers(start_reg, length)
                regs_l = regs_l[::-1]
                for i in range(0, length, 2):
                    data.append(self.regs2float(regs_l[i : i + 2]))
                self.logger.info(f"Registros leídos del PLC ok")
                break
            except Exception as e:
                self.logger.info(f"Intento {attempts + 1} de lectura fallido: {e}")
                attempts += 1
                time.sleep(1)
        if attempts == max_attempts:
            self.logger.info(
                f"No se pudo leer los registros del PLC después de {max_attempts} intentos."
            )
            return None
        return data
