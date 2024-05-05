import time

from pymodbus.client import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from pyModbusTCP.client import ModbusClient

from modbus_adv_toolbox.utils.logger import Logger


class AccutechRTU:
    _instance = None

    def __new__(cls, ip_address, port):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(ip_address, port)
        return cls._instance

    def _initialize(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        self.tcp_client = ModbusTcpClient(
            host=ip_address, port=port, auto_open=True, auto_close=True
        )
        self.rtu_client = ModbusClient(
            host=ip_address, port=port, auto_open=True, auto_close=True
        )
        self.logger = Logger(name="Modbus-Toolbox-Accutech")._set_logger()
        self.test_connection()

    def update_ip_and_port(self, new_ip_address, new_port):
        self.ip_address = new_ip_address
        self.port = new_port
        self.tcp_client = ModbusTcpClient(
            host=new_ip_address, port=new_port, auto_open=True, auto_close=True
        )
        self.rtu_client = ModbusClient(
            host=new_ip_address, port=new_port, auto_open=True, auto_close=True
        )

    def test_connection(self, max_attempts=3):
        for attempt in range(1, max_attempts + 1):
            if self.tcp_client.connect():
                self.logger.info(f"Conexión exitosa en el intento {attempt}")
                return True
            else:
                self.logger.info(f"Intento {attempt} de conexión fallido")
                if attempt < max_attempts:
                    self.logger.info("Reintentando...")
                    time.sleep(1)
        self.logger.info("No se pudo establecer la conexión después de varios intentos")
        return False

    def read_specific_register(self, register):
        regs_l = self.rtu_client.read_holding_registers(register, 2)
        dec = BinaryPayloadDecoder.fromRegisters(
            regs_l, byteorder=Endian.Little, wordorder=Endian.Big
        )
        value = dec.decode_32bit_float()
        return value

    def read_values_fast(self, amount=30):
        data = []
        for i in range(1, amount + 1):
            modbus_register_address = 5 + (i * 10)
            data.append(self.read_specific_register(modbus_register_address))
        return data

    def read_values_by_rfid(self, amount=30):
        data = []
        for rfid in range(1, amount + 1):
            data.append(self.read_register_for_rfid(rfid))
        return data

    def read_values(self, amount=30, max_attempts=2):
        data = []
        for i in range(1, amount + 1):
            modbus_register_address = 5 + (i * 10)
            value = None
            attempts = 0
            while attempts < max_attempts:
                try:
                    value = self.read_specific_register(modbus_register_address)
                    break
                except Exception as e:
                    self.logger.info(f"Intento {attempts + 1} de lectura fallido: {e}")
                    attempts += 1
                    time.sleep(1)
            if value is not None:
                data.append(value)
            else:
                self.logger.info(
                    f"No se pudo leer el valor del registro {modbus_register_address} después de {max_attempts} intentos."
                )
                data.append(None)
        return data

    def read_acc(self, amount=30):
        data = []
        # try to read the initial modbus register if it fails, add 0 to all data values and return
        try:
            self.read_specific_register(15)
            # self.logger.info(f"Valor inicial: {initial_value}")
            for i in range(1, amount + 1):
                modbus_register_address = 5 + (i * 10)
                value = self.read_specific_register(modbus_register_address)
                if value is not None:
                    data.append(value)
                else:
                    self.logger.info(
                        f"No se pudo leer el valor del registro numero: {modbus_register_address}"
                    )
                    data.append(None)
            self.logger.info(f"Valores Accutech leidos correctamente")
            return data
        except:
            self.logger.info(
                f"No se pudo leer el valor del registro inicial, se retornan None en todos los valores"
            )
            for i in range(1, amount + 1):
                data.append(None)
            return data

    def write_specific_register(self, register, value):
        builder = BinaryPayloadBuilder(byteorder=Endian.Little, wordorder=Endian.Big)
        builder.add_32bit_float(value)
        payload = builder.build()
        self.client.write_registers(register - 2, payload, skip_encode=True)

    def write_register_for_rfid(self, rfid, value):
        modbus_register_address = 5 + (rfid * 10)
        builder = BinaryPayloadBuilder(byteorder=Endian.Little, wordorder=Endian.Big)
        builder.add_32bit_float(value)
        regs_to_write = builder.to_registers()
        result = self.client.write_multiple_registers(
            modbus_register_address, regs_to_write
        )
        if result:
            self.logger.info(f"Valor {value} escrito para RFID {rfid}")
        else:
            self.logger.info(f"Error al escribir registros para RFID {rfid}")

    def read_register_for_rfid(self, rfid):
        modbus_register_address = 5 + (rfid * 10)
        regs_l = self.client.read_holding_registers(modbus_register_address, 2)
        if regs_l:
            dec = BinaryPayloadDecoder.fromRegisters(
                regs_l, byteorder=Endian.Little, wordorder=Endian.Big
            )
            value = dec.decode_32bit_float()
            return value
        else:
            return None
